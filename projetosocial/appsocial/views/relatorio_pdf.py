from io import BytesIO
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # CORRIGIDO: era "from pyexpat.errors import messages"
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, timedelta
import calendar


@login_required
def relatorio_pdf_form(request):
    """
    Gera relatório a partir dos parâmetros GET: ?ano=2025&mes=3 (mes opcional)
    Valida que a data não seja futura.
    """
    ano_str = request.GET.get('ano')
    if not ano_str or not ano_str.isdigit():
        messages.error(request, 'Ano inválido.')
        return redirect('dashboard')
    ano = int(ano_str)

    mes_str = request.GET.get('mes')
    if mes_str and mes_str.isdigit():
        mes = int(mes_str)
        if mes < 1 or mes > 12:
            messages.error(request, 'Mês inválido (1-12).')
            return redirect('dashboard')
    else:
        mes = None

    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month

    if ano > ano_atual:
        messages.error(request, f'Não é possível gerar relatório para o ano {ano} (ano superior ao atual).')
        return redirect('dashboard')

    if ano == ano_atual and mes is not None and mes > mes_atual:
        messages.error(request, f'Não é possível gerar relatório para o mês {mes} do ano {ano} porque ainda não chegou.')
        return redirect('dashboard')

    if ano == ano_atual and mes is None:
        messages.error(request, f'Não é possível gerar relatório anual para o ano {ano} porque ainda não terminou. '
                                 f'Utilize um mês específico (até {mes_atual}) ou aguarde o final do ano.')
        return redirect('dashboard')

    return relatorio_pdf(request, ano, mes)


@login_required
def relatorio_pdf(request, ano, mes=None):
    ano = int(ano)
    if mes:
        mes = int(mes)
        titulo = f"Relatório Mensal - {calendar.month_name[mes]} de {ano}"
        periodo = f"Período: {calendar.month_name[mes]} {ano}"
    else:
        titulo = f"Relatório Anual - {ano}"
        periodo = f"Período: Ano {ano}"

    if mes:
        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = datetime(ano, mes + 1, 1) - timedelta(days=1)
    else:
        data_inicio = datetime(ano, 1, 1)
        data_fim = datetime(ano, 12, 31)

    with connection.cursor() as cursor:

        # ----- Totais gerais -----
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT CASE WHEN u.id_tipo_utente = 2 AND u.data_criacao BETWEEN %s AND %s THEN u.id_utente END) AS total_idosos,
                COUNT(DISTINCT CASE WHEN u.id_tipo_utente = 1 AND u.data_criacao BETWEEN %s AND %s THEN u.id_utente END) AS total_socioeconomicos,
                COUNT(DISTINCT i.id_intervencao) AS total_intervencoes,
                COUNT(DISTINCT c.id_contacto) AS total_contactos
            FROM UTENTES u
            LEFT JOIN INTERVENCAO i ON i.data_intervencao BETWEEN %s AND %s
            LEFT JOIN CONTACTO c ON c.data_contacto BETWEEN %s AND %s
            WHERE (u.data_criacao BETWEEN %s AND %s OR i.id_intervencao IS NOT NULL OR c.id_contacto IS NOT NULL)
        """, [
            data_inicio, data_fim,  # para idosos
            data_inicio, data_fim,  # para socioeconómicos
            data_inicio, data_fim,  # para intervenções
            data_inicio, data_fim,  # para contactos
            data_inicio, data_fim   # para a cláusula WHERE
        ])
        row = cursor.fetchone()
        totais = {
            'total_idosos': row[0] or 0,
            'total_socioeconomicos': row[1] or 0,
            'total_intervencoes': row[2] or 0,
            'total_contactos': row[3] or 0,
        }

        # ----- Problemáticas no período -----
        cursor.execute("""
            SELECT p.nome_problematica, COUNT(*) AS total_ocorrencias
            FROM ter t
            JOIN problematicas_identificadas p ON p.id_problematica = t.id_problematica
            WHERE t.data_inicio BETWEEN %s AND %s
            GROUP BY p.nome_problematica
            ORDER BY total_ocorrencias DESC
        """, [data_inicio, data_fim])
        problematicas = cursor.fetchall()
        problematica_labels = [p[0] for p in problematicas]
        problematica_data = [p[1] for p in problematicas]

        # ----- Idosos isolados (estado no último dia do período) -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'nome' AS nome,
                    ( (hi.snapshot_json->'principal'->>'idade')::float )::int AS idade,
                    hi.snapshot_json->'principal'->>'nivel_isolamento' AS nivel_isolamento,
                    (hi.snapshot_json->'principal'->>'vive_sozinho')::boolean AS vive_sozinho
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT nome, idade, nivel_isolamento, vive_sozinho
            FROM snapshots_mais_recentes
            WHERE nivel_isolamento = 'Elevado' AND vive_sozinho = true
        """, [data_fim, data_inicio, data_fim])
        idosos_isolados = cursor.fetchall()
        total_isolados = len(idosos_isolados)

        # ----- Perfil etário - Socioeconómicos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hus.id_utente)
                    hus.id_utente,
                    ( (hus.snapshot_json->'principal'->>'idade')::float )::int AS idade
                FROM historico_utente_socioeconomico hus
                JOIN UTENTES u ON hus.id_utente = u.id_utente
                WHERE hus.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hus.id_utente, hus.data_historico DESC
            )
            SELECT 
                CASE 
                    WHEN idade BETWEEN 0 AND 17 THEN '0-17'
                    WHEN idade BETWEEN 18 AND 24 THEN '18-24'
                    WHEN idade BETWEEN 25 AND 34 THEN '25-34'
                    WHEN idade BETWEEN 35 AND 44 THEN '35-44'
                    WHEN idade BETWEEN 45 AND 54 THEN '45-54'
                    WHEN idade BETWEEN 55 AND 64 THEN '55-64'
                    ELSE '65+'
                END AS faixa_etaria,
                COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY faixa_etaria
            ORDER BY MIN(idade)
        """, [data_fim, data_inicio, data_fim])
        idades_socio = cursor.fetchall()
        socio_labels = [i[0] for i in idades_socio]
        socio_data = [i[1] for i in idades_socio]

        # ----- Perfil etário - Idosos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    ( (hi.snapshot_json->'principal'->>'idade')::float )::int AS idade
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT 
                CASE 
                    WHEN idade BETWEEN 65 AND 74 THEN '65-74'
                    WHEN idade BETWEEN 75 AND 84 THEN '75-84'
                    ELSE '85+'
                END AS faixa_etaria,
                COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY faixa_etaria
            ORDER BY MIN(idade)
        """, [data_fim, data_inicio, data_fim])
        idades_idosos = cursor.fetchall()
        idosos_faixa_labels = [i[0] for i in idades_idosos]
        idosos_faixa_data = [i[1] for i in idades_idosos]

        # ----- Género socioeconómicos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hus.id_utente)
                    hus.id_utente,
                    hus.snapshot_json->'principal'->>'sexo' AS genero
                FROM historico_utente_socioeconomico hus
                JOIN UTENTES u ON hus.id_utente = u.id_utente
                WHERE hus.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hus.id_utente, hus.data_historico DESC
            )
            SELECT genero, COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY genero
        """, [data_fim, data_inicio, data_fim])
        genero_socio = cursor.fetchall()
        genero_socio_labels = [g[0] for g in genero_socio]
        genero_socio_data = [g[1] for g in genero_socio]

        # ----- Género idosos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'sexo' AS genero
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT genero, COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY genero
        """, [data_fim, data_inicio, data_fim])
        genero_idosos = cursor.fetchall()
        genero_idosos_labels = [g[0] for g in genero_idosos]
        genero_idosos_data = [g[1] for g in genero_idosos]

        # ----- Autonomia dos idosos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'grau_autonomia' AS autonomia
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT autonomia, COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY autonomia
            ORDER BY total DESC
        """, [data_fim, data_inicio, data_fim])
        autonomia = cursor.fetchall()
        autonomia_labels = [a[0] for a in autonomia]
        autonomia_data = [a[1] for a in autonomia]

        # ----- Nível de isolamento dos idosos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'nivel_isolamento' AS isolamento
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT isolamento, COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY isolamento
            ORDER BY total DESC
        """, [data_fim, data_inicio, data_fim])
        isolamento = cursor.fetchall()
        isolamento_labels = [i[0] for i in isolamento]
        isolamento_data = [i[1] for i in isolamento]

        # ----- Risco social -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hus.id_utente)
                    hus.id_utente,
                    (hus.snapshot_json->'principal'->>'risco_social')::boolean AS risco_social
                FROM historico_utente_socioeconomico hus
                JOIN UTENTES u ON hus.id_utente = u.id_utente
                WHERE hus.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hus.id_utente, hus.data_historico DESC
            )
            SELECT 
                CASE WHEN risco_social THEN 'Em risco' ELSE 'Estavel' END AS situacao,
                COUNT(*) AS total
            FROM snapshots_mais_recentes
            GROUP BY risco_social
        """, [data_fim, data_inicio, data_fim])
        risco = cursor.fetchall()
        risco_labels = [r[0] for r in risco]
        risco_data = [r[1] for r in risco]

        # ----- Total de idosos que vivem sozinhos -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    (hi.snapshot_json->'principal'->>'vive_sozinho')::boolean AS vive_sozinho
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s    
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT COUNT(*) FROM snapshots_mais_recentes WHERE vive_sozinho = true
        """, [data_fim, data_inicio, data_fim])
        row = cursor.fetchone()
        total_vive_sozinho = row[0] if row else 0

        # ----- Total de idosos com dependência -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'grau_autonomia' AS autonomia
                FROM historico_idoso hi
                JOIN UTENTES u ON hi.id_utente = u.id_utente
                WHERE hi.data_historico <= %s
                    AND u.data_criacao BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT COUNT(*) FROM snapshots_mais_recentes WHERE autonomia != 'Autonomo'
        """, [data_fim, data_inicio, data_fim])
        row = cursor.fetchone()
        total_dependentes = row[0] if row else 0

        # ----- Zonas -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hus.id_utente)
                    hus.id_utente,
                    hus.snapshot_json->'principal'->>'zona' AS zona,
                    (hus.snapshot_json->'principal'->>'risco_social')::boolean AS risco_social
                FROM historico_utente_socioeconomico hus
                JOIN UTENTES u ON hus.id_utente = u.id_utente
                WHERE u.data_criacao BETWEEN %s AND %s
                  AND hus.data_historico <= %s
                ORDER BY hus.id_utente, hus.data_historico DESC
            )
            SELECT 
                COALESCE(zona, 'Desconhecida') AS zona,
                COUNT(*) AS total,
                COUNT(CASE WHEN risco_social THEN 1 END) AS risco
            FROM snapshots_mais_recentes
            GROUP BY zona
            ORDER BY zona
        """, [data_inicio, data_fim, data_fim])
        zonas_utentes = cursor.fetchall()

        # ----- Tipos de intervenção -----
        cursor.execute("""
            SELECT ti.nome_tipo_intervencao AS tipo, COUNT(*) AS total
            FROM intervencao i
            JOIN tipo_intervencao ti ON i.id_tipo_intervencao = ti.id_tipo_intervencao
            WHERE i.data_intervencao BETWEEN %s AND %s
            GROUP BY ti.nome_tipo_intervencao
            ORDER BY total DESC
        """, [data_inicio, data_fim])
        tipos_interv = cursor.fetchall()
        tipos_interv_labels = [t[0] for t in tipos_interv]
        tipos_interv_data = [t[1] for t in tipos_interv]

        # ----- Programas -----
        cursor.execute("""
            SELECT p.programa, COUNT(*) AS total
            FROM intervencao i
            JOIN programa p ON i.id_programa = p.id_programa
            WHERE i.data_intervencao BETWEEN %s AND %s
            GROUP BY p.programa
            ORDER BY total DESC
        """, [data_inicio, data_fim])
        programas = cursor.fetchall()
        programas_labels = [p[0] for p in programas]
        programas_data = [p[1] for p in programas]

        # ----- Evolução de problemáticas -----
        cursor.execute("""
            SELECT ano_mes, novos_casos, ativos_fim_mes
            FROM vw_evolucao_problematicas
            ORDER BY mes
        """)
        evolucao_all = cursor.fetchall()
        if mes:
            evolucao = [row for row in evolucao_all if row[0] == f"{ano}-{mes:02d}"]
        else:
            evolucao = [row for row in evolucao_all if row[0].startswith(f"{ano}-")]
        evolucao_labels = [row[0] for row in evolucao]
        evolucao_novos = [row[1] for row in evolucao]
        evolucao_ativos = [row[2] for row in evolucao]

        # ----- Taxa de reincidência -----
        cursor.execute("""
            WITH 
            primeiras_periodo AS (
                SELECT DISTINCT id_utente, id_problematica, data_inicio AS primeira_data
                FROM ter t1
                WHERE t1.data_inicio BETWEEN %s AND %s
                  AND NOT EXISTS (
                      SELECT 1 FROM ter t0
                      WHERE t0.id_utente = t1.id_utente
                        AND t0.id_problematica = t1.id_problematica
                        AND t0.data_inicio < t1.data_inicio
                  )
            ),
            reincidentes AS (
                SELECT DISTINCT pp.id_utente, pp.id_problematica
                FROM primeiras_periodo pp
                JOIN ter t2 ON pp.id_utente = t2.id_utente AND pp.id_problematica = t2.id_problematica
                WHERE t2.data_inicio > pp.primeira_data
                  AND EXISTS (
                      SELECT 1 FROM ter t_res 
                      WHERE t_res.id_utente = pp.id_utente
                        AND t_res.id_problematica = pp.id_problematica
                        AND t_res.data_fim IS NOT NULL
                        AND t_res.data_fim < t2.data_inicio
                  )
            ),
            total_casos_unicos AS (
                SELECT COUNT(*) AS total FROM primeiras_periodo
            ),
            total_reincidentes AS (
                SELECT COUNT(*) AS total FROM reincidentes
            )
            SELECT 
                (SELECT total FROM total_reincidentes) AS casos_com_reincidencia,
                (SELECT total FROM total_casos_unicos) AS total_casos_unicos,
                ROUND(100.0 * (SELECT total FROM total_reincidentes) / 
                      NULLIF((SELECT total FROM total_casos_unicos), 0), 2) AS taxa_percentual
        """, [data_inicio, data_fim])
        row_reinc = cursor.fetchone()
        reincidencia_total = {
            'casos_com_reincidencia': row_reinc[0] or 0,
            'total_casos_unicos': row_reinc[1] or 0,
            'taxa_percentual': row_reinc[2] or 0,
        }

        # ----- Respostas nos encaminhamentos -----
        cursor.execute("""
            SELECT tr.descricao_tipo_resposta, COUNT(e.id_encaminhamento) AS total_ocorrencias
            FROM encaminhamentos_rede e
            JOIN tipo_resposta tr ON e.id_tipo_resposta = tr.id_tipo_resposta
            WHERE e.data_resposta BETWEEN %s AND %s
            GROUP BY tr.descricao_tipo_resposta
            ORDER BY total_ocorrencias DESC
        """, [data_inicio, data_fim])
        respostas = cursor.fetchall()
        respostas_labels = [r[0] for r in respostas]
        respostas_data = [r[1] for r in respostas]

        # ----- Top 10 idosos com mais contactos -----
        # CORRIGIDO: vírgula em falta entre "idade" e "z.descricao_zona_utente"
        cursor.execute("""
            SELECT u.nome_utente, COUNT(c.id_contacto) AS num_contactos,
                   EXTRACT(YEAR FROM AGE(%s, u.DATA_NASCIMENTO)) AS idade,
                   z.descricao_zona_utente AS zona
            FROM contacto c
            JOIN utentes_idosos ui ON c.id_utente = ui.id_utente
            JOIN utentes u ON ui.id_utente = u.id_utente
            JOIN zona_utente z ON u.id_zona_utente = z.id_zona_utente
            WHERE c.data_contacto BETWEEN %s AND %s
            GROUP BY u.nome_utente, u.data_nascimento, z.descricao_zona_utente
            ORDER BY num_contactos DESC
            LIMIT 10
        """, [data_fim, data_inicio, data_fim])
        mais_contactos = cursor.fetchall()

        # ----- Quedas repetidas no período (mínimo 2 quedas) -----
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(%s, u.DATA_NASCIMENTO)) AS idade,
                z.DESCRICAO_ZONA_UTENTE AS zona,
                COUNT(q.ID_QUEDA) AS total_quedas,
                MAX(q.DATA_QUEDA) AS ultima_queda
            FROM UTENTES u
            JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            LEFT JOIN QUEDAS_IDOSO q ON u.ID_UTENTE = q.ID_UTENTE
            WHERE q.DATA_QUEDA BETWEEN %s AND %s
            GROUP BY u.ID_UTENTE, u.NOME_UTENTE, z.DESCRICAO_ZONA_UTENTE
            HAVING COUNT(q.ID_QUEDA) >= 2
            ORDER BY total_quedas DESC, ultima_queda DESC
        """, [data_fim, data_inicio, data_fim])
        quedas_repetidas = cursor.fetchall()

        # ----- Falta de rede de suporte (estado no período, usando snapshot mais recente dentro do período) -----
        cursor.execute("""
            WITH snapshots_mais_recentes AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'nome' AS nome,
                    ( (hi.snapshot_json->'principal'->>'idade')::float )::int AS idade,
                    hi.snapshot_json->'principal'->>'zona' AS zona,
                    (hi.snapshot_json->'principal'->>'vive_sozinho')::boolean AS vive_sozinho,
                    hi.snapshot_json->'principal'->>'contacto_emergencia' AS contacto_emergencia,
                    hi.snapshot_json->'principal'->>'familiar_referencia' AS familiar_referencia
                FROM historico_idoso hi
                WHERE hi.data_historico BETWEEN %s AND %s   -- filtrar pelo período
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT 
                id_utente,
                nome,
                idade,
                zona,
                vive_sozinho,
                contacto_emergencia,
                familiar_referencia
            FROM snapshots_mais_recentes
            WHERE vive_sozinho = true
            AND (contacto_emergencia IS NULL OR contacto_emergencia = '')
            AND (familiar_referencia IS NULL OR familiar_referencia = '')
        """, [data_inicio, data_fim])   # dois parâmetros: início e fim do período
        falta_rede_suporte = cursor.fetchall()

        # ----- Visitas prioritárias (apenas eventos e snapshots dentro do período) -----
        cursor.execute("""
            WITH 
            snapshots_idosos AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'nome' AS nome,
                    ( (hi.snapshot_json->'principal'->>'idade')::float )::int AS idade,
                    hi.snapshot_json->'principal'->>'zona' AS zona,
                    hi.snapshot_json->'principal'->>'nivel_isolamento' AS nivel_isolamento,
                    (hi.snapshot_json->'principal'->>'vive_sozinho')::boolean AS vive_sozinho,
                    hi.snapshot_json->'principal'->>'contacto_emergencia' AS contacto_emergencia,
                    hi.snapshot_json->'principal'->>'familiar_referencia' AS familiar_referencia
                FROM historico_idoso hi
                WHERE hi.data_historico BETWEEN %s AND %s   -- filtrar snapshots pelo período
                ORDER BY hi.id_utente, hi.data_historico DESC
            ),
            prioridade1 AS (
                SELECT 
                    id_utente,
                    nome AS nome_utente,
                    idade,
                    zona,
                    'Isolamento elevado + vive sozinho' AS motivo,
                    1 AS prioridade
                FROM snapshots_idosos
                WHERE nivel_isolamento = 'Elevado' AND vive_sozinho = true
            ),
            quedas_periodo AS (
                SELECT 
                    q.id_utente,
                    COUNT(q.id_queda) AS total_quedas
                FROM quedas_idoso q
                WHERE q.data_queda BETWEEN %s AND %s   -- quedas no período
                GROUP BY q.id_utente
                HAVING COUNT(q.id_queda) >= 2
            ),
            prioridade2 AS (
                SELECT 
                    s.id_utente,
                    s.nome AS nome_utente,
                    s.idade,
                    s.zona,
                    'Quedas repetidas' AS motivo,
                    2 AS prioridade
                FROM snapshots_idosos s
                JOIN quedas_periodo qp ON s.id_utente = qp.id_utente
            ),
            prioridade3 AS (
                SELECT 
                    id_utente,
                    nome AS nome_utente,
                    idade,
                    zona,
                    'Falta de rede de suporte' AS motivo,
                    3 AS prioridade
                FROM snapshots_idosos
                WHERE vive_sozinho = true
                AND (contacto_emergencia IS NULL OR contacto_emergencia = '')
                AND (familiar_referencia IS NULL OR familiar_referencia = '')
            )
            SELECT * FROM prioridade1
            UNION
            SELECT * FROM prioridade2
            UNION
            SELECT * FROM prioridade3
            ORDER BY prioridade, idade DESC
        """, [data_inicio, data_fim, data_inicio, data_fim])   # 1º par: snapshots, 2º par: quedas
        visitas_prioritarias = cursor.fetchall()

        # ----- Idosos sem contacto no período (apenas criados no período) -----
        cursor.execute("""
            SELECT u.nome_utente, NULL AS ultimo_contacto
            FROM utentes u
            JOIN utentes_idosos ui ON u.id_utente = ui.id_utente
            WHERE u.data_criacao BETWEEN %s AND %s
            AND NOT EXISTS (
                SELECT 1 FROM contacto c
                WHERE c.id_utente = u.id_utente
                    AND c.data_contacto BETWEEN %s AND %s
            )
            ORDER BY u.nome_utente
        """, [data_inicio, data_fim, data_inicio, data_fim])
        idosos_sem_contacto = cursor.fetchall()

        # ----- Melhorias após participação -----
        cursor.execute("""
            WITH snapshots_inicio AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'nome' AS nome,
                    hi.snapshot_json->'principal'->>'grau_autonomia' AS grau_inicio,
                    hi.snapshot_json->'principal'->>'nivel_isolamento' AS isolamento_inicio
                FROM historico_idoso hi
                WHERE hi.data_historico >= %s
                ORDER BY hi.id_utente, hi.data_historico ASC
            ),
            snapshots_fim AS (
                SELECT DISTINCT ON (hi.id_utente)
                    hi.id_utente,
                    hi.snapshot_json->'principal'->>'grau_autonomia' AS grau_fim,
                    hi.snapshot_json->'principal'->>'nivel_isolamento' AS isolamento_fim
                FROM historico_idoso hi
                WHERE hi.data_historico <= %s
                ORDER BY hi.id_utente, hi.data_historico DESC
            )
            SELECT 
                i.nome AS nome_utente,
                i.grau_inicio,
                f.grau_fim,
                i.isolamento_inicio,
                f.isolamento_fim,
                CASE 
                    WHEN (i.grau_inicio = 'Dependente' AND f.grau_fim IN ('Parcialmente dependente', 'Autónomo'))
                    OR (i.grau_inicio = 'Parcialmente dependente' AND f.grau_fim = 'Autónomo')
                    OR (i.isolamento_inicio = 'Elevado' AND f.isolamento_fim IN ('Moderado', 'Nenhum'))
                    OR (i.isolamento_inicio = 'Moderado' AND f.isolamento_fim = 'Nenhum')
                    THEN 1 ELSE 0
                END AS melhorou
            FROM snapshots_inicio i
            JOIN snapshots_fim f ON i.id_utente = f.id_utente
            WHERE i.grau_inicio IS NOT NULL AND f.grau_fim IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM contacto c
                WHERE c.id_utente = i.id_utente
                    AND c.data_contacto BETWEEN %s AND %s
            )
        """, [data_inicio, data_fim, data_inicio, data_fim])
        melhorias = cursor.fetchall()

        # ----- Agravamento do grau de dependência (qualquer piora dentro do período) -----
        cursor.execute("""
            WITH snapshots_periodo AS (
                SELECT 
                    hi.id_utente,
                    hi.data_historico,
                    hi.snapshot_json->'principal'->>'nome' AS nome,
                    ( (hi.snapshot_json->'principal'->>'idade')::float )::int AS idade,
                    hi.snapshot_json->'principal'->>'grau_autonomia' AS grau,
                    hi.snapshot_json->'principal'->>'zona' AS zona,
                    CASE 
                        WHEN hi.snapshot_json->'principal'->>'grau_autonomia' = 'Autónomo' THEN 1
                        WHEN hi.snapshot_json->'principal'->>'grau_autonomia' = 'Parcialmente dependente' THEN 2
                        WHEN hi.snapshot_json->'principal'->>'grau_autonomia' = 'Dependente' THEN 3
                        ELSE 0
                    END AS nivel
                FROM historico_idoso hi
                WHERE hi.data_historico BETWEEN %s AND %s
                ORDER BY hi.id_utente, hi.data_historico
            ),
            agravamentos AS (
                SELECT DISTINCT s1.id_utente, s1.nome, s1.idade, s1.zona,
                    s1.grau AS grau_anterior,
                    s2.grau AS grau_atual
                FROM snapshots_periodo s1
                JOIN snapshots_periodo s2 ON s1.id_utente = s2.id_utente AND s1.data_historico < s2.data_historico
                WHERE s1.nivel < s2.nivel
            )
            SELECT nome, idade, zona, grau_anterior, grau_atual
            FROM agravamentos
            ORDER BY nome
        """, [data_inicio, data_fim])
        agravamentos = cursor.fetchall()
    # =========================================================
    # --- Construção do PDF ---
    # =========================================================
    response = HttpResponse(content_type='application/pdf')
    if mes:
        filename = f"relatorio_mensal_{ano}_{mes:02d}.pdf"
    else:
        filename = f"relatorio_anual_{ano}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
    )
    styles = getSampleStyleSheet()

    titulo_estilo = ParagraphStyle(
        'TituloEstilo', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#0d6efd'),
        alignment=TA_CENTER, spaceAfter=20,
    )
    subtitulo_estilo = ParagraphStyle(
        'SubtituloEstilo', parent=styles['Heading2'],
        fontSize=14, textColor=colors.black,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=8,
    )
    normal_estilo = ParagraphStyle('NormalEstilo', parent=styles['Normal'], fontSize=9, leading=12)
    celula_estilo = ParagraphStyle('CelulaEstilo', parent=styles['Normal'], fontSize=8, leading=10)

    TABLE_STYLE = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ])

    def tabela(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TABLE_STYLE)
        return t

    story = []

    # ---- Cabeçalho ----
    story.append(Paragraph(titulo, titulo_estilo))
    story.append(Paragraph(periodo, normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Indicadores Gerais ----
    story.append(Paragraph("Indicadores Gerais", subtitulo_estilo))
    story.append(Paragraph(f"<b>Total de Idosos (criados no período):</b> {totais['total_idosos']}", normal_estilo))
    story.append(Paragraph(f"<b>Total de Utentes Socioeconómicos (criados no período):</b> {totais['total_socioeconomicos']}", normal_estilo))
    story.append(Paragraph(f"<b>Total de Intervenções (ocorridas no período):</b> {totais['total_intervencoes']}", normal_estilo))
    story.append(Paragraph(f"<b>Total de Contactos (ocorridos no período):</b> {totais['total_contactos']}", normal_estilo))
    # ADICIONADO: métricas de idosos que antes estavam em falta
    story.append(Paragraph(f"<b>Total dos Idosos criados no período que Vivem Sozinhos (estado a {data_fim.strftime('%d/%m/%Y')}):</b> {total_vive_sozinho}", normal_estilo))
    story.append(Paragraph(f"<b>Total de Idosos criados no período com Dependência (estado a {data_fim.strftime('%d/%m/%Y')}):</b> {total_dependentes}", normal_estilo))
    story.append(Paragraph(f"<b>Total de Idosos criados no período em Isolamento Elevado e que Vivem Sozinhos (estado a {data_fim.strftime('%d/%m/%Y')}):</b> {total_isolados}", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Problemáticas ----
    story.append(Paragraph("Problemáticas Mais Frequentes (identificadas no período)", subtitulo_estilo))
    if problematica_labels:
        table_data = [[Paragraph("Problematica", celula_estilo), Paragraph("Ocorrencias", celula_estilo)]]
        for label, val in zip(problematica_labels, problematica_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [10*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem problemáticas registadas no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Evolução de Problemáticas ----
    story.append(Paragraph("Evolução de Problemáticas (últimos meses)", subtitulo_estilo))
    if evolucao_labels:
        table_data = [[Paragraph("Mes", celula_estilo), Paragraph("Novos Casos", celula_estilo), Paragraph("Ativos (fim do mes)", celula_estilo)]]
        for label, novos, ativos in zip(evolucao_labels, evolucao_novos, evolucao_ativos):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(novos), celula_estilo), Paragraph(str(ativos), celula_estilo)])
        story.append(KeepTogether(tabela(table_data, [4*cm, 4*cm, 4*cm])))
    else:
        story.append(Paragraph("Sem dados de evolucao para o periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Taxa de Reincidência ----
    story.append(Paragraph("Taxa de Reincidência (problemáticas surgidas no periodo)", subtitulo_estilo))
    story.append(Paragraph(f"<b>Casos com reincidência:</b> {reincidencia_total['casos_com_reincidencia']}", normal_estilo))
    story.append(Paragraph(f"<b>Total de casos únicos (primeira ocorrencia no periodo):</b> {reincidencia_total['total_casos_unicos']}", normal_estilo))
    story.append(Paragraph(f"<b>Taxa de reincidência:</b> {reincidencia_total['taxa_percentual']}%", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Tipos de Intervenção ----
    story.append(Paragraph("Tipos de Intervenção Mais Utilizados (no período)", subtitulo_estilo))
    if tipos_interv_labels:
        table_data = [[Paragraph("Tipo", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(tipos_interv_labels, tipos_interv_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [8*cm, 3*cm]))
    else:
        story.append(Paragraph("Nenhuma intervencao no periodo.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- Programas ----
    story.append(Paragraph("Programas Mais Utilizados (no período)", subtitulo_estilo))
    if programas_labels:
        table_data = [[Paragraph("Programa", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(programas_labels, programas_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [8*cm, 3*cm]))
    else:
        story.append(Paragraph("Nenhum programa no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Respostas nos Encaminhamentos ----
    story.append(Paragraph("Respostas nos Encaminhamentos (com data no período)", subtitulo_estilo))
    if respostas_labels:
        table_data = [[Paragraph("Tipo de Resposta", celula_estilo), Paragraph("Ocorrências", celula_estilo)]]
        for label, val in zip(respostas_labels, respostas_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [8*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem respostas de encaminhamento no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Perfil Demográfico - Socioeconómicos ----
    story.append(Paragraph(f"Perfil Demografico - Socioeconomicos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if socio_labels:
        table_data = [[Paragraph("Faixa Etaria", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(socio_labels, socio_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [6*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem utentes socioeconomicos no periodo.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- Perfil Demográfico - Idosos ----
    story.append(Paragraph(f"Perfil Demografico - Idosos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if idosos_faixa_labels:
        table_data = [[Paragraph("Faixa Etaria", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(idosos_faixa_labels, idosos_faixa_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [6*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem idosos no periodo.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- Distribuição por Género ----
    story.append(Paragraph(f"Distribuicao por Genero (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    texto_socio = ", ".join([f"{g}: {v}" for g, v in zip(genero_socio_labels, genero_socio_data)]) or "Sem dados"
    texto_idosos_gen = ", ".join([f"{g}: {v}" for g, v in zip(genero_idosos_labels, genero_idosos_data)]) or "Sem dados"
    story.append(Paragraph(f"<b>Socioeconomicos:</b> {texto_socio}", normal_estilo))
    story.append(Paragraph(f"<b>Idosos:</b> {texto_idosos_gen}", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- Autonomia dos Idosos ----
    story.append(Paragraph(f"Nivel de Autonomia dos Idosos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if autonomia_labels:
        table_data = [[Paragraph("Grau de Autonomia", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(autonomia_labels, autonomia_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [6*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem dados de autonomia.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- Isolamento dos Idosos ----
    story.append(Paragraph(f"Nivel de Isolamento dos Idosos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if isolamento_labels:
        table_data = [[Paragraph("Nivel", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(isolamento_labels, isolamento_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [6*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem dados de isolamento.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # ---- ADICIONADO: Risco Social (Socioeconómicos) ----
    story.append(Paragraph(f"Risco Social - Socioeconomicos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if risco_labels:
        table_data = [[Paragraph("Situacao", celula_estilo), Paragraph("Total", celula_estilo)]]
        for label, val in zip(risco_labels, risco_data):
            table_data.append([Paragraph(label, celula_estilo), Paragraph(str(val), celula_estilo)])
        story.append(tabela(table_data, [6*cm, 3*cm]))
    else:
        story.append(Paragraph("Sem dados de risco social.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Idosos em Isolamento Elevado e que Vivem Sozinhos ----
    story.append(Paragraph(f"Idosos em Isolamento Elevado e que Vivem Sozinhos (estado a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if idosos_isolados:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("Idade", celula_estilo),
            Paragraph("Nivel Isolamento", celula_estilo), Paragraph("Vive Sozinho", celula_estilo),
        ]]
        for iso in idosos_isolados:
            table_data.append([
                Paragraph(iso[0] or "-", celula_estilo),
                Paragraph(str(iso[1]) if iso[1] is not None else "-", celula_estilo),
                Paragraph(iso[2] or "-", celula_estilo),
                Paragraph("Sim" if iso[3] else "Nao", celula_estilo),
            ])
        story.append(tabela(table_data, [5*cm, 2.5*cm, 3.5*cm, 2.5*cm]))
    else:
        story.append(Paragraph("Nenhum idoso nesta situacao.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- ADICIONADO: Quedas Repetidas ----
    story.append(Paragraph(f"Idosos com Quedas Repetidas no Periodo (minimo 2 quedas)", subtitulo_estilo))
    if quedas_repetidas:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("Idade", celula_estilo),
            Paragraph("Zona", celula_estilo), Paragraph("Total Quedas", celula_estilo),
            Paragraph("Ultima Queda", celula_estilo),
        ]]
        for q in quedas_repetidas:
            ultima_queda = q[5].strftime('%d/%m/%Y') if q[5] else "-"
            table_data.append([
                Paragraph(q[1] or "-", celula_estilo),
                Paragraph(str(int(q[2])) if q[2] is not None else "-", celula_estilo),
                Paragraph(q[3] or "-", celula_estilo),
                Paragraph(str(q[4]), celula_estilo),
                Paragraph(ultima_queda, celula_estilo),
            ])
        story.append(tabela(table_data, [5*cm, 2*cm, 4*cm, 3*cm, 3*cm]))
    else:
        story.append(Paragraph("Nenhum idoso com quedas repetidas no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Falta de Rede de Suporte ----
    story.append(Paragraph("Falta de Rede de Suporte (vive sozinho e sem contactos de emergencia)", subtitulo_estilo))
    if falta_rede_suporte:
        table_data = [[Paragraph("Nome", celula_estilo), Paragraph("Idade", celula_estilo), Paragraph("Zona", celula_estilo)]]
        for f in falta_rede_suporte:
            table_data.append([
                Paragraph(str(f[1]) if len(f) > 1 and f[1] else "-", celula_estilo),
                Paragraph(str(f[2]) if len(f) > 2 and f[2] is not None else "-", celula_estilo),
                Paragraph(str(f[3]) if len(f) > 3 and f[3] else "-", celula_estilo),
            ])
        story.append(tabela(table_data, [6*cm, 3*cm, 6*cm]))
    else:
        story.append(Paragraph("Nenhum idoso nesta situacao.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Visitas Prioritárias ----
    story.append(Paragraph("Situacoes que precisam de visita prioritaria", subtitulo_estilo))
    if visitas_prioritarias:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("Idade", celula_estilo),
            Paragraph("Zona", celula_estilo), Paragraph("Motivo", celula_estilo),
            Paragraph("Prioridade", celula_estilo),
        ]]
        # CORRIGIDO: emojis removidos — ReportLab não os renderiza corretamente
        prioridade_map = {1: "Alta", 2: "Media", 3: "Baixa"}
        for v in visitas_prioritarias:
            table_data.append([
                Paragraph(str(v[1]) if len(v) > 1 and v[1] else "-", celula_estilo),
                Paragraph(str(v[2]) if len(v) > 2 and v[2] is not None else "-", celula_estilo),
                Paragraph(str(v[3]) if len(v) > 3 and v[3] else "-", celula_estilo),
                Paragraph(str(v[4]) if len(v) > 4 and v[4] else "-", celula_estilo),
                Paragraph(prioridade_map.get(v[5], str(v[5])) if len(v) > 5 else "-", celula_estilo),
            ])
        story.append(tabela(table_data, [4*cm, 2*cm, 3*cm, 4*cm, 2.5*cm]))
    else:
        story.append(Paragraph("Nenhuma situacao prioritaria.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Idosos sem Contacto no Período ----
    story.append(Paragraph("Idosos sem contacto no periodo", subtitulo_estilo))
    if idosos_sem_contacto:
        table_data = [[Paragraph("Nome", celula_estilo)]]
        for iso in idosos_sem_contacto:
            table_data.append([Paragraph(iso[0] or "-", celula_estilo)])
        story.append(tabela(table_data, [10*cm]))
    else:
        story.append(Paragraph("Todos os idosos tiveram pelo menos um contacto no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Top 10 Idosos com Mais Contactos ----
    story.append(Paragraph("Top 10 Idosos com mais contactos (no periodo)", subtitulo_estilo))
    if mais_contactos:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("No contactos", celula_estilo),
            Paragraph("Idade", celula_estilo), Paragraph("Zona", celula_estilo),
        ]]
        for c in mais_contactos:
            table_data.append([
                Paragraph(c[0] or "-", celula_estilo),
                Paragraph(str(c[1]), celula_estilo),
                Paragraph(str(int(c[2])) if c[2] is not None else "-", celula_estilo),
                Paragraph(c[3] or "-", celula_estilo),
            ])
        story.append(tabela(table_data, [5*cm, 3*cm, 2.5*cm, 4*cm]))
    else:
        story.append(Paragraph("Nenhum contacto no periodo.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Agravamento do Grau de Dependência ----
    story.append(Paragraph("Agravamento do Grau de Dependencia", subtitulo_estilo))
    if agravamentos:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("Idade", celula_estilo),
            Paragraph("Zona", celula_estilo), Paragraph("Grau Anterior", celula_estilo),
            Paragraph("Grau Atual", celula_estilo),
        ]]
        for a in agravamentos:
            table_data.append([
                Paragraph(a[0] or "-", celula_estilo),
                Paragraph(str(int(a[1])) if a[1] is not None else "-", celula_estilo),
                Paragraph(a[2] or "-", celula_estilo),
                Paragraph(a[3] or "-", celula_estilo),
                Paragraph(a[4] or "-", celula_estilo),
            ])
        story.append(tabela(table_data, [4*cm, 2*cm, 3*cm, 3*cm, 3*cm]))
    else:
        story.append(Paragraph("Nenhum agravamento registado.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Melhorias Após Participação ----
    story.append(Paragraph("Melhorias apos participacao (comparacao primeiro vs ultimo snapshot)", subtitulo_estilo))
    if melhorias:
        table_data = [[
            Paragraph("Nome", celula_estilo), Paragraph("Grau inicial", celula_estilo),
            Paragraph("Grau atual", celula_estilo), Paragraph("Isolamento inicial", celula_estilo),
            Paragraph("Isolamento atual", celula_estilo), Paragraph("Melhorou?", celula_estilo),
        ]]
        for m in melhorias:
            table_data.append([
                Paragraph(m[0] or "-", celula_estilo),
                Paragraph(m[1] or "-", celula_estilo),
                Paragraph(m[2] or "-", celula_estilo),
                Paragraph(m[3] or "-", celula_estilo),
                Paragraph(m[4] or "-", celula_estilo),
                Paragraph("Sim" if m[5] else "Nao", celula_estilo),
            ])
        story.append(tabela(table_data, [4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm]))
    else:
        story.append(Paragraph("Sem dados de melhoria.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # ---- Utentes por Zona e Risco Social ----
    story.append(Paragraph(f"Utentes por Zona e Risco Social (utentes criados no periodo, zona a {data_fim.strftime('%d/%m/%Y')})", subtitulo_estilo))
    if zonas_utentes:
        table_data = [[
            Paragraph("Zona", celula_estilo),
            Paragraph("Total de Utentes", celula_estilo),
            Paragraph("Com Risco Social", celula_estilo),
        ]]
        for zona in zonas_utentes:
            table_data.append([
                Paragraph(zona[0] or "-", celula_estilo),
                Paragraph(str(zona[1]), celula_estilo),
                Paragraph(str(zona[2]), celula_estilo),
            ])
        story.append(tabela(table_data, [5*cm, 4*cm, 4*cm]))
    else:
        story.append(Paragraph("Sem dados de zonas.", normal_estilo))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Relatorio gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_estilo))

    doc.build(story)
    return response