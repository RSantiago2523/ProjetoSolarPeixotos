import json
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from datetime import date, datetime
from decimal import Decimal


def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    return None

def parse_datetime(dt_str):
    if not dt_str:
        return None
    # Tenta primeiro o formato ISO 8601 com 'T'
    try:
        return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        # Se falhar, tenta com espaço (fallback)
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

def guardar_historico_utente(request, id_utente):
    """Guarda o estado atual do utente no histórico (JSON serializável)."""
    with connection.cursor() as cursor:
        # 1. Dados principais
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
                n.DESCRICAO_NACIONALIDADE,
                z.DESCRICAO_ZONA_UTENTE,
                sh.DESCRICAO_SITUACAO_HABITACIONAL,
                sl.DESCRICAO_SITUACAO_LABORAL,
                tr.NOME_TIPO_RENDIMENTO,
                ta.DESCRICAO_TIPOLOGIA,
                usec.RISCO_SOCIAL,
                usec.OBSERVACOES_UTENTE,
                usec.CRITERIO_RISCO
            FROM UTENTES u
            JOIN UTENTES_SOCIO_ECONOMICAS usec ON u.ID_UTENTE = usec.ID_UTENTE
            JOIN NACIONALIDADE n ON usec.ID_NACIONALIDADE = n.ID_NACIONALIDADE
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            JOIN SITUACAO_HABITACIONAL sh ON usec.ID_SITUACAO_HABITACIONAL = sh.ID_SITUACAO_HABITACIONAL
            JOIN SITUACAO_LABORAL sl ON usec.ID_SITUACAO_LABORAL = sl.ID_SITUACAO_LABORAL
            JOIN TIPO_RENDIMENTO tr ON usec.ID_TIPO_RENDIMENTO = tr.ID_TIPO_RENDIMENTO
            JOIN TIPOLOGIA_AGREGADO_FAMILIAR ta ON usec.ID_TIPOLOGIA = ta.ID_TIPOLOGIA
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        principal = cursor.fetchone()
        if not principal:
            return

        # 2. Intervenções
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                ti.NOME_TIPO_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                to_char(i.DATA_INTERVENCAO, 'YYYY-MM-DD HH24:MI:SS') as DATA_INTERVENCAO,
                i.OBSERVACOES_INTERVENCAO
            FROM INTERVENCAO i
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            JOIN PARTICIPAR pa ON i.ID_INTERVENCAO = pa.ID_INTERVENCAO
            WHERE pa.ID_UTENTE = %s
            ORDER BY i.DATA_INTERVENCAO DESC
        """, [id_utente])
        intervencoes = cursor.fetchall()

        # 3. Problemáticas
        cursor.execute("""
            SELECT 
                p.NOME_PROBLEMATICA,
                to_char(t.DATA_INICIO, 'YYYY-MM-DD') as DATA_INICIO,
                to_char(t.DATA_FIM, 'YYYY-MM-DD') as DATA_FIM,
                CASE WHEN t.DATA_FIM IS NULL THEN 'Ativa' ELSE 'Resolvida' END AS ESTADO,
                t.ID_INTERVENCAO,
                to_char(i.DATA_INTERVENCAO, 'YYYY-MM-DD HH24:MI:SS') as INTERV_DATA,
                ti.NOME_TIPO_INTERVENCAO AS INTERV_TIPO
            FROM TER t
            JOIN PROBLEMATICAS_IDENTIFICADAS p ON t.ID_PROBLEMATICA = p.ID_PROBLEMATICA
            LEFT JOIN INTERVENCAO i ON t.ID_INTERVENCAO = i.ID_INTERVENCAO
            LEFT JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            WHERE t.ID_UTENTE = %s
            ORDER BY t.DATA_INICIO DESC
        """, [id_utente])
        problematicas = cursor.fetchall()

        # 4. Membros
        cursor.execute("""
            SELECT NOME_MEMBRO, ANO_NASCIMENTO, GRAU_PARENTESCO
            FROM MEMBROS_AGREGADO_FAMILIAR
            WHERE ID_UTENTE = %s
        """, [id_utente])
        membros = cursor.fetchall()

        # 5. Despesas fixas
        cursor.execute("""
            SELECT td.DESCRICAO_TIPO_DESPESA, df.VALOR_DESPESA
            FROM DESPESAS_FIXAS df
            JOIN TIPO_DESPESA td ON df.ID_TIPO_DESPESA = td.ID_TIPO_DESPESA
            WHERE df.ID_UTENTE = %s
        """, [id_utente])
        despesas = cursor.fetchall()

        # 6. Escalões
        cursor.execute("""
            SELECT TIPO_ESCALAO, VALOR_EXATO
            FROM ESCALAO_RENDIMENTOS
            WHERE ID_UTENTE = %s
            ORDER BY ID_ESCALAO DESC
        """, [id_utente])
        escaloes = cursor.fetchall()

        # Função para converter Decimal, date, datetime
        def convert(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(v) for v in obj]
            else:
                return obj

        snapshot = {
            'principal': {
                'id_utente': principal[0],
                'nome': principal[1],
                'idade': principal[2],
                'nacionalidade': principal[3],
                'zona': principal[4],
                'situacao_habitacional': principal[5],
                'situacao_laboral': principal[6],
                'tipo_rendimento': principal[7],
                'tipologia_agregado': principal[8],
                'risco_social': principal[9],
                'observacoes': principal[10] or '',
                'criterio_risco': principal[11] or '',
            },
            'intervencoes': [
                {
                    'id': i[0],
                    'tipo': i[1] or '',
                    'entidade': i[2] or '',
                    'programa': i[3] or '',
                    'data': i[4] or '',
                    'observacoes': i[5] or ''
                } for i in intervencoes
            ],
            'problematicas': [
                {
                    'nome': p[0] or '',
                    'data_inicio': p[1] or '',
                    'data_fim': p[2] or '',
                    'estado': p[3] or '',
                    'id_intervencao': p[4],
                    'interv_data': p[5],
                    'interv_tipo': p[6]
                } for p in problematicas
            ],
            'membros_agregado': [{'nome': m[0] or '', 'ano': m[1], 'parentesco': m[2] or ''} for m in membros],
            'despesas': [{'descricao': d[0] or '', 'valor': d[1]} for d in despesas],
            'escaloes': [{'tipo': e[0] or '', 'valor': e[1]} for e in escaloes],
        }

        snapshot_serializavel = convert(snapshot)

        usuario = request.user.username if request.user.is_authenticated else 'sistema'
        cursor.execute("""
            INSERT INTO historico_utente_socioeconomico (id_utente, data_historico, usuario, snapshot_json)
            VALUES (%s, %s, %s, %s)
        """, [id_utente, datetime.now(), usuario, json.dumps(snapshot_serializavel, ensure_ascii=False)])


@login_required
def historico_utente_lista(request, id_utente):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_historico, data_historico, usuario
            FROM historico_utente_socioeconomico
            WHERE id_utente = %s
            ORDER BY data_historico DESC
        """, [id_utente])
        historicos = cursor.fetchall()

    # Obter nome do utente para exibir no título
    with connection.cursor() as cursor:
        cursor.execute("SELECT nome_utente FROM utentes WHERE id_utente = %s", [id_utente])
        row = cursor.fetchone()
        nome_utente = row[0] if row else "Utente"

    return render(request, 'historicos/historico_lista.html', {
        'historicos': historicos,
        'id_utente': id_utente,
        'nome_utente': nome_utente,
    })

@login_required
def historico_utente_detalhe(request, id_utente, id_historico):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT snapshot_json, data_historico, usuario
            FROM historico_utente_socioeconomico
            WHERE id_historico = %s AND id_utente = %s
        """, [id_historico, id_utente])
        row = cursor.fetchone()
        if not row:
            messages.error(request, 'Versão histórica não encontrada.')
            return redirect('socioeconomicos_detalhe', id_utente=id_utente)

    snapshot = json.loads(row[0])
    data_historico = row[1]
    usuario = row[2]

    # Converter os dados do snapshot para tuplas (o template espera tuplas)
    principal = snapshot['principal']
    utente = (
        principal['id_utente'],
        principal['nome'],
        principal['idade'],
        principal['nacionalidade'],
        principal['zona'],
        principal['situacao_habitacional'],
        principal['situacao_laboral'],
        principal['tipo_rendimento'],
        principal['tipologia_agregado'],
        principal['risco_social'],
        principal['observacoes'],
        principal['criterio_risco'],
    )
    intervencoes = [
        (i['id'], i['tipo'], i['entidade'], i['programa'], i['data'], i['observacoes'])
        for i in snapshot['intervencoes']
    ]
    problematicas = [
        (p['nome'], parse_date(p['data_inicio']), parse_date(p['data_fim']), p['estado'], p['id_intervencao'], parse_datetime(p['interv_data']), p['interv_tipo'])
        for p in snapshot['problematicas']
    ]
    membros_agregado = [(m['nome'], m['ano'], m['parentesco']) for m in snapshot['membros_agregado']]
    despesas = [(d['descricao'], d['valor']) for d in snapshot['despesas']]
    escaloes = [(e['tipo'], e['valor']) for e in snapshot['escaloes']]

    return render(request, 'historicos/historico_detalhe.html', {
        'utente': utente,
        'intervencoes': intervencoes,
        'problematicas': problematicas,
        'membros_agregado': membros_agregado,
        'despesas': despesas,
        'escaloes': escaloes,
        'data_historico': data_historico,
        'usuario': usuario,
        'id_utente': id_utente,
    })

@login_required
def historico_utente_limpar_tudo(request, id_utente):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM historico_utente_socioeconomico WHERE id_utente = %s", [id_utente])
    messages.success(request, "Todos os registos de histórico foram eliminados.")
    return redirect('historico_utente_lista', id_utente=id_utente)

def guardar_historico_idoso(request, id_utente):
    """Guarda o estado atual do idoso no histórico (JSON serializável)."""
    with connection.cursor() as cursor:
        # 1. Dados principais (igual à consulta do detalhe)
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS IDADE,
                g.DESCRICAO_GENERO AS SEXO,
                z.DESCRICAO_ZONA_UTENTE AS ZONA,
                ec.DESCRICAO_ESTADO_CIVIL,
                ga.NOME_GRAU_AUTONOMIA AS GRAU_AUTONOMIA,
                m.NOME_MOBILIDADE AS MOBILIDADE,
                ni.NIVEL_ISOLAMENTO,
                rf.DESCRICAO_RELACAO_FAMILIA,
                fcs.DESCRICAO_FREQUENCIA_CONTACTO_SOCIAL AS FREQUENCIA_CONTACTO_SOCIAL,
                th.DESCRICAO_TIPO AS TIPO_HABITACAO,
                ui.VIVE_SOZINHO,
                ui.CONTACTO_EMERGENCIA,
                ui.FAMILIAR_REFERENCIA,
                ui.MEDICACAO_DIARIA,
                ui.DIFICULDADE_ACESSO_SAUDE,
                ui.ACOMPANHAMENTO_REG,
                ui.PARTICIPA_ATIVIDADES_FR,
                ui.TRISTESA_DEPRESSAO,
                ui.LUTO_RECENTE,
                ui.AQUECIMENTO_ADEQ_INV,
                ui.SEGURANCA,
                ui.NECESSIDADE_ADPTACOES
            FROM UTENTES u
            JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
            JOIN GENERO g ON u.ID_GENERO = g.ID_GENERO
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            JOIN ESTADO_CIVIL ec ON ui.ID_ESTADO_CIVIL = ec.ID_ESTADO_CIVIL
            JOIN GRAU_AUTONOMIA ga ON ui.ID_GRAU_AUTONOMIA = ga.ID_GRAU_AUTONOMIA
            JOIN MOBILIDADE m ON ui.ID_MOBILIDADE = m.ID_MOBILIDADE
            JOIN NIVEL_ISOLAMENTO ni ON ui.ID_NIVEL_ISOLAMENTO = ni.ID_NIVEL_ISOLAMENTO
            JOIN RELACAO_FAMILIA rf ON ui.ID_RELACAO_FAMILIA = rf.ID_RELACAO_FAMILIA
            JOIN FREQUENCIA_CONTACTO_SOCIAL fcs ON ui.ID_FREQUENCIA_CONTACTO_SOCIAL = fcs.ID_FREQUENCIA_CONTACTO_SOCIAL
            JOIN TIPO_HABITACAO th ON ui.ID_TIPO_HABITACAO = th.ID_TIPO_HABITACAO
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        principal = cursor.fetchone()

        # 2. Atividades da vida diária (lista de textos)
        cursor.execute("SELECT DESCRICAO_ATIVIDADE_DIARIA FROM ATIVIDADES_DIARIA WHERE ID_UTENTE = %s", [id_utente])
        atividades = [row[0] for row in cursor.fetchall()]

        # 3. Doenças crónicas (lista)
        cursor.execute("""
            SELECT dc.DESCRICAO_DOENCA_CRONICA
            FROM DOENCAS_IDOSOS di
            JOIN DOENCAS_CRONICAS dc ON di.ID_DOENCA_CRONICA = dc.ID_DOENCA_CRONICA
            WHERE di.ID_UTENTE = %s
        """, [id_utente])
        doencas = [row[0] for row in cursor.fetchall()]

        # 4. Barreiras arquitetónicas (lista)
        cursor.execute("""
            SELECT ba.DESCRICAO_BARREIRA_ARQUITETONICA
            FROM BARREIRAS_IDOSOS bi
            JOIN BARREIRAS_ARQUITETONICAS ba ON bi.ID_BARREIRA_ARQUITETONICA = ba.ID_BARREIRA_ARQUITETONICA
            WHERE bi.ID_UTENTE = %s
        """, [id_utente])
        barreiras = [row[0] for row in cursor.fetchall()]

        # 5. Contactos (lista de dicionários)
        cursor.execute("""
            SELECT c.ID_CONTACTO, c.DATA_CONTACTO, tc.NOME_TIPO_CONTACTO, fc.DESCRICAO_FREQUENCIA_CONTACTO, c.OBSERVACOES_CONTACTO
            FROM CONTACTO c
            JOIN TIPO_CONTACTO tc ON c.ID_TIPO_CONTACTO = tc.ID_TIPO_CONTACTO
            JOIN FREQUENCIA_CONTACTO fc ON c.ID_FREQUENCIA_CONTACTO = fc.ID_FREQUENCIA_CONTACTO
            WHERE c.ID_UTENTE = %s
            ORDER BY c.DATA_CONTACTO DESC
        """, [id_utente])
        contactos_raw = cursor.fetchall()
        contactos = [
            {
                'id': r[0],
                'data': r[1].isoformat() if r[1] else None,
                'tipo': r[2],
                'frequencia': r[3],
                'observacoes': r[4] or ''
            } for r in contactos_raw
        ]

        # 6. Quedas (lista de dicionários)
        cursor.execute("SELECT DATA_QUEDA, OBSERVACOES_QUEDA FROM QUEDAS_IDOSO WHERE ID_UTENTE = %s ORDER BY DATA_QUEDA DESC", [id_utente])
        quedas_raw = cursor.fetchall()
        quedas = [
            {'data': q[0].isoformat() if q[0] else None, 'observacoes': q[1] or ''}
            for q in quedas_raw
        ]

        # 7. Sinais de fragilidade (lista)
        cursor.execute("""
            SELECT sf.DESCRICAO_FRAGILIDADE
            FROM FRAGILIDADE_IDOSO fi
            JOIN SINAIS_FRAGILIDADE sf ON fi.ID_SINAL_FRAGILIDADE = sf.ID_SINAL_FRAGILIDADE
            WHERE fi.ID_UTENTE = %s
        """, [id_utente])
        fragilidades = [row[0] for row in cursor.fetchall()]

        # Função de conversão
        def convert(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert(v) for v in obj]
            else:
                return obj

        snapshot = {
            'principal': {
                'id_utente': principal[0],
                'nome': principal[1],
                'idade': principal[2],
                'sexo': principal[3],
                'zona': principal[4],
                'estado_civil': principal[5],
                'grau_autonomia': principal[6],
                'mobilidade': principal[7],
                'nivel_isolamento': principal[8],
                'relacao_familia': principal[9],
                'frequencia_contacto_social': principal[10],
                'tipo_habitacao': principal[11],
                'vive_sozinho': principal[12],
                'contacto_emergencia': principal[13] or '',
                'familiar_referencia': principal[14] or '',
                'medicacao_diaria': principal[15],
                'dificuldade_acesso_saude': principal[16],
                'acompanhamento_reg': principal[17],
                'participa_atividades_fr': principal[18],
                'tristesa_depressao': principal[19],
                'luto_recente': principal[20],
                'aquecimento_adeq_inv': principal[21],
                'seguranca': principal[22] or '',
                'necessidade_adptacoes': principal[23] or '',
            },
            'atividades': atividades,
            'doencas': doencas,
            'barreiras': barreiras,
            'contactos': contactos,
            'quedas': quedas,
            'fragilidades': fragilidades,
        }

        snapshot_serializavel = convert(snapshot)

        usuario = request.user.username if request.user.is_authenticated else 'sistema'
        cursor.execute("""
            INSERT INTO historico_idoso (id_utente, data_historico, usuario, snapshot_json)
            VALUES (%s, %s, %s, %s)
        """, [id_utente, datetime.now(), usuario, json.dumps(snapshot_serializavel, ensure_ascii=False)])

@login_required
def historico_idoso_lista(request, id_utente):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_historico, data_historico, usuario
            FROM historico_idoso
            WHERE id_utente = %s
            ORDER BY data_historico DESC
        """, [id_utente])
        historicos = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT nome_utente FROM utentes WHERE id_utente = %s", [id_utente])
        row = cursor.fetchone()
        nome = row[0] if row else "Idoso"

    return render(request, 'historicos/historico_lista_idoso.html', {
        'historicos': historicos,
        'id_utente': id_utente,
        'nome_utente': nome,
    })


@login_required
def historico_idoso_detalhe(request, id_utente, id_historico):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT snapshot_json, data_historico, usuario
            FROM historico_idoso
            WHERE id_historico = %s AND id_utente = %s
        """, [id_historico, id_utente])
        row = cursor.fetchone()
        if not row:
            messages.error(request, 'Versão histórica não encontrada.')
            return redirect('historico_idoso_lista', id_utente=id_utente)

    snapshot = json.loads(row[0])
    data_historico = row[1]
    usuario = row[2]

    # Converter o snapshot para a estrutura que o template detalhe espera
    p = snapshot['principal']
    utente = (
        p['id_utente'],
        p['nome'],
        p['idade'],
        p['sexo'],
        p['zona'],
        p['estado_civil'],
        p['grau_autonomia'],
        p['mobilidade'],
        p['nivel_isolamento'],
        p['relacao_familia'],
        p['frequencia_contacto_social'],
        p['tipo_habitacao'],
        p['vive_sozinho'],
        p['contacto_emergencia'],
        p['familiar_referencia'],
        p['medicacao_diaria'],
        p['dificuldade_acesso_saude'],
        p['acompanhamento_reg'],
        p['participa_atividades_fr'],
        p['tristesa_depressao'],
        p['luto_recente'],
        p['aquecimento_adeq_inv'],
        p['seguranca'],
        p['necessidade_adptacoes'],
    )

    # Conversão de datas dos contactos
    contactos = []
    for c in snapshot.get('contactos', []):
        contactos.append((
            c['id'],
            parse_datetime(c['data']),
            c['tipo'],
            c['frequencia'],
            c['observacoes'],
        ))

    quedas = [(parse_date(q['data']), q['observacoes']) for q in snapshot.get('quedas', [])]

    # Listas simples
    atividades = [(a,) for a in snapshot.get('atividades', [])]
    doencas = [(d,) for d in snapshot.get('doencas', [])]
    barreiras = [(b,) for b in snapshot.get('barreiras', [])]
    fragilidades = [(f,) for f in snapshot.get('fragilidades', [])]

    return render(request, 'historicos/historico_detalhe_idoso.html', {
        'utente': utente,
        'atividades': atividades,
        'doencas': doencas,
        'barreiras': barreiras,
        'contactos': contactos,
        'quedas': quedas,
        'fragilidades': fragilidades,
        'data_historico': data_historico,
        'usuario': usuario,
        'id_utente': id_utente,
    })


@login_required
def historico_idoso_limpar_tudo(request, id_utente):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM historico_idoso WHERE id_utente = %s", [id_utente])
    messages.success(request, "Todos os registos de histórico foram eliminados.")
    return redirect('historico_idoso_lista', id_utente=id_utente)