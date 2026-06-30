from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    with connection.cursor() as cursor:
        # 1. Totais gerais
        cursor.execute("SELECT * FROM vw_totais_gerais")
        row = cursor.fetchone()
        totais = {
            'total_idosos': row[0],
            'total_socioeconomicos': row[1],
            'total_intervencoes': row[2],
            'total_contactos': row[3],
        }

        # 2. Intervenções por mês
        cursor.execute("SELECT ano, mes, total FROM vw_intervencoes_mes_ano ORDER BY ano, mes")
        intervencoes_mes = cursor.fetchall()
        intervencoes_labels = [f"{int(ano)}-{int(mes):02d}" for ano, mes, _ in intervencoes_mes]
        intervencoes_data = [total for _, _, total in intervencoes_mes]

        # 3. Contactos por mês
        cursor.execute("SELECT ano, mes, total_contactos FROM vw_contactos_mes_ano ORDER BY ano, mes")
        contactos_mes = cursor.fetchall()
        contactos_labels = [f"{int(ano)}-{int(mes):02d}" for ano, mes, _ in contactos_mes]
        contactos_data = [total for _, _, total in contactos_mes]

        # 4. Problemáticas mais frequentes
        cursor.execute("SELECT problematica, total_ocorrencias FROM vw_problematicas_ocorridas")
        problematicas = cursor.fetchall()
        problematica_labels = [p[0] for p in problematicas]
        problematica_data = [p[1] for p in problematicas]

        # 5. Idosos isolados (lista)
        cursor.execute("SELECT nome_utente, idade, nivel_isolamento, vive_sozinho FROM vw_idosos_isolados")
        idosos_isolados = cursor.fetchall()

        # 6. Número total de idosos isolados
        cursor.execute("SELECT total_idosos_isolados FROM vw_numero_idosos_isolados")
        total_isolados = cursor.fetchone()[0] if cursor.rowcount else 0

        # 7. Idades socioeconómicos
        cursor.execute("SELECT faixa_etaria, total FROM vw_idades_socioeconomicos ORDER BY faixa_etaria")
        idades_socio = cursor.fetchall()
        socio_labels = [i[0] for i in idades_socio]
        socio_data = [i[1] for i in idades_socio]

        # 8. Idades idosos
        cursor.execute("SELECT faixa_etaria, total FROM vw_idades_idosos ORDER BY faixa_etaria")
        idades_idosos = cursor.fetchall()
        idosos_faixa_labels = [i[0] for i in idades_idosos]
        idosos_faixa_data = [i[1] for i in idades_idosos]

        # 9. Género socioeconómicos
        cursor.execute("SELECT genero, total FROM vw_genero_socioeconomicos")
        genero_socio = cursor.fetchall()
        genero_socio_labels = [g[0] for g in genero_socio]
        genero_socio_data = [g[1] for g in genero_socio]

        # 10. Género idosos
        cursor.execute("SELECT genero, total FROM vw_genero_idosos")
        genero_idosos = cursor.fetchall()
        genero_idosos_labels = [g[0] for g in genero_idosos]
        genero_idosos_data = [g[1] for g in genero_idosos]

        # 11. Autonomia idosos
        cursor.execute("SELECT grau_autonomia, total FROM vw_autonomia_idosos")
        autonomia = cursor.fetchall()
        autonomia_labels = [a[0] for a in autonomia]
        autonomia_data = [a[1] for a in autonomia]

        # 12. Tipos de intervenção
        cursor.execute("SELECT tipo, total FROM vw_tipos_intervencao_utilizados")
        tipos_interv = cursor.fetchall()
        tipos_interv_labels = [t[0] for t in tipos_interv]
        tipos_interv_data = [t[1] for t in tipos_interv]

        # 13. Programas
        cursor.execute("SELECT programa, total FROM vw_programas_utilizados")
        programas = cursor.fetchall()
        programas_labels = [p[0] for p in programas]
        programas_data = [p[1] for p in programas]

        # 14. Risco social
        cursor.execute("SELECT situacao, total FROM vw_risco_social")
        risco = cursor.fetchall()
        risco_labels = [r[0] for r in risco]
        risco_data = [r[1] for r in risco]

        # 15. Nível de isolamento idosos
        cursor.execute("SELECT nivel_isolamento, total FROM vw_nivel_isolamento_idosos")
        isolamento = cursor.fetchall()
        isolamento_labels = [i[0] for i in isolamento]
        isolamento_data = [i[1] for i in isolamento]

        # 16. Evolução de problemáticas (novos casos e ativos por mês)
        cursor.execute("""
            SELECT 
                ano_mes,
                novos_casos,
                ativos_fim_mes
            FROM vw_evolucao_problematicas
            ORDER BY mes
        """)
        evolucao = cursor.fetchall()
        evolucao_labels = [row[0] for row in evolucao]          # ex: "2024-01"
        evolucao_novos = [row[1] for row in evolucao]           # novos casos
        evolucao_ativos = [row[2] for row in evolucao]          # ativos fim do mês

        # 17. Taxa de reincidência por problemática
        cursor.execute("""
            SELECT 
                nome_problematica,
                total_utentes,
                utentes_reincidentes,
                taxa_reincidencia_percentual
            FROM vw_taxa_reincidencia_por_problematica
            ORDER BY taxa_reincidencia_percentual DESC
        """)
        reincidencia = cursor.fetchall()

        # 18. Respostas mais utilizadas nos encaminhamentos
        cursor.execute("""
            SELECT tipo_resposta, total_ocorrencias
            FROM vw_respostas_mais_utilizadas
            ORDER BY total_ocorrencias DESC
        """)
        respostas_encaminhamentos = cursor.fetchall()
        respostas_labels = [row[0] for row in respostas_encaminhamentos]
        respostas_data = [row[1] for row in respostas_encaminhamentos]

        # 19. Idosos sem contacto há mais de 4 semanas
        cursor.execute("SELECT * FROM vw_idosos_sem_contacto_4semanas")
        idosos_sem_contacto = cursor.fetchall()

        # 20. Quedas repetidas
        cursor.execute("SELECT * FROM vw_quedas_repetidas")
        quedas_repetidas = cursor.fetchall()

        # 21. Falta de rede de suporte
        cursor.execute("SELECT * FROM vw_falta_rede_suporte")
        falta_rede_suporte = cursor.fetchall()

        # 22. Visitas prioritárias
        cursor.execute("SELECT * FROM vw_visita_prioritaria")
        visitas_prioritarias = cursor.fetchall()

        # 23. Zonas com total de utentes e risco social
        cursor.execute("SELECT descricao_zona_utente, total, risco FROM vw_zona_utentes ORDER BY descricao_zona_utente")
        zonas_utentes = cursor.fetchall()

        # ----- 24. Agravamento do grau de dependência -----
        cursor.execute("""
            SELECT nome_utente, idade, zona, grau_atual, grau_anterior
            FROM vw_agravamento_dependencia
        """)
        agravamentos = cursor.fetchall()

        # ----- 25. Total de idosos que vivem sozinhos -----
        cursor.execute("SELECT total_vive_sozinho FROM vw_vive_sozinho")
        total_vive_sozinho = cursor.fetchone()[0]

        # ----- 26. Total de idosos com dependência -----
        cursor.execute("SELECT total_dependentes FROM vw_dependentes")
        total_dependentes = cursor.fetchone()[0]

        # ----- 27. Top 10 idosos com mais contactos -----
        cursor.execute("""
            SELECT nome_utente, num_contactos, idade, zona
            FROM vw_mais_contactos
        """)
        mais_contactos = cursor.fetchall()

        # ----- 28. Melhorias após participação -----
        cursor.execute("""
            SELECT nome_utente, grau_inicial, grau_final, isolamento_inicial, isolamento_final, melhorou
            FROM vw_melhorias
        """)
        melhorias = cursor.fetchall()

    context = {
        'totais': totais,
        'intervencoes_labels': intervencoes_labels,
        'intervencoes_data': intervencoes_data,
        'contactos_labels': contactos_labels,
        'contactos_data': contactos_data,
        'problematica_labels': problematica_labels,
        'problematica_data': problematica_data,
        'idosos_isolados': idosos_isolados,
        'total_isolados': total_isolados,
        'socio_labels': socio_labels,
        'socio_data': socio_data,
        'idosos_faixa_labels': idosos_faixa_labels,
        'idosos_faixa_data': idosos_faixa_data,
        'genero_socio_labels': genero_socio_labels,
        'genero_socio_data': genero_socio_data,
        'genero_idosos_labels': genero_idosos_labels,
        'genero_idosos_data': genero_idosos_data,
        'autonomia_labels': autonomia_labels,
        'autonomia_data': autonomia_data,
        'tipos_interv_labels': tipos_interv_labels,
        'tipos_interv_data': tipos_interv_data,
        'programas_labels': programas_labels,
        'programas_data': programas_data,
        'risco_labels': risco_labels,
        'risco_data': risco_data,
        'isolamento_labels': isolamento_labels,
        'isolamento_data': isolamento_data,
        'evolucao_labels': evolucao_labels,
        'evolucao_novos': evolucao_novos,
        'evolucao_ativos': evolucao_ativos,
        'reincidencia': reincidencia,
        'respostas_labels': respostas_labels,
        'respostas_data': respostas_data,
        'idosos_sem_contacto': idosos_sem_contacto,
        'quedas_repetidas': quedas_repetidas,
        'falta_rede_suporte': falta_rede_suporte,
        'visitas_prioritarias': visitas_prioritarias,
        'zonas_utentes': zonas_utentes,
        'agravamentos': agravamentos,
        'total_vive_sozinho': total_vive_sozinho,
        'total_dependentes': total_dependentes,
        'mais_contactos': mais_contactos,
        'melhorias': melhorias,
    }
    return render(request, 'dashboard/dashboard.html', context)