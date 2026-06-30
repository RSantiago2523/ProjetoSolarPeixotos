from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from .historico import guardar_historico_idoso
from .. import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#Listar Idosos
@login_required
def idosos_lista(request):
    nome_filter = request.GET.get('nome', '').strip()
    page_number = request.GET.get('page', 1)

    query = """
        SELECT 
            u.ID_UTENTE,
            u.NOME_UTENTE,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS IDADE,
            g.DESCRICAO_GENERO AS SEXO,
            ec.DESCRICAO_ESTADO_CIVIL,
            ui.VIVE_SOZINHO,
            z.DESCRICAO_ZONA_UTENTE AS ZONA,
            ui.CONTACTO_EMERGENCIA
        FROM UTENTES u
        JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
        JOIN GENERO g ON u.ID_GENERO = g.ID_GENERO
        JOIN ESTADO_CIVIL ec ON ui.ID_ESTADO_CIVIL = ec.ID_ESTADO_CIVIL
        JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
    """
    params = []

    if nome_filter:
        query += " WHERE u.NOME_UTENTE ILIKE %s"
        params.append(f'%{nome_filter}%')

    query += " ORDER BY u.ID_UTENTE"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        todos_idosos = cursor.fetchall()

    # Paginação (50 registos por página)
    paginator = Paginator(todos_idosos, 20)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'idosos/lista_idosos.html', {
        'idosos': page_obj,
        'filtro_nome': nome_filter,
    })

#VER UM UTENTE IDOSO
@login_required
def idosos_detalhe(request, id_utente):
    with connection.cursor() as cursor:
        # 1. Dados básicos do utente (UTENTES + UTENTES_IDOSOS + tabelas relacionadas)
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
        utente = cursor.fetchone()
        if not utente:
            messages.error(request, 'Idoso não encontrado.')
            return redirect('idosos_lista')

        # 2. Atividades da vida diária (tabela ATIVIDADES_DIARIA)
        cursor.execute("""
            SELECT DESCRICAO_ATIVIDADE_DIARIA
            FROM ATIVIDADES_DIARIA
            WHERE ID_UTENTE = %s
        """, [id_utente])
        atividades = cursor.fetchall()

        # 3. Doenças crónicas
        cursor.execute("""
            SELECT dc.DESCRICAO_DOENCA_CRONICA
            FROM DOENCAS_IDOSOS di
            JOIN DOENCAS_CRONICAS dc ON di.ID_DOENCA_CRONICA = dc.ID_DOENCA_CRONICA
            WHERE di.ID_UTENTE = %s
        """, [id_utente])
        doencas = cursor.fetchall()

        # 4. Barreiras arquitetónicas
        cursor.execute("""
            SELECT ba.DESCRICAO_BARREIRA_ARQUITETONICA
            FROM BARREIRAS_IDOSOS bi
            JOIN BARREIRAS_ARQUITETONICAS ba ON bi.ID_BARREIRA_ARQUITETONICA = ba.ID_BARREIRA_ARQUITETONICA
            WHERE bi.ID_UTENTE = %s
        """, [id_utente])
        barreiras = cursor.fetchall()

        # 5. Contactos realizados
        cursor.execute("""
            SELECT
                c.ID_CONTACTO, 
                c.DATA_CONTACTO,
                tc.NOME_TIPO_CONTACTO,
                fc.DESCRICAO_FREQUENCIA_CONTACTO,
                c.OBSERVACOES_CONTACTO
            FROM CONTACTO c
            JOIN TIPO_CONTACTO tc ON c.ID_TIPO_CONTACTO = tc.ID_TIPO_CONTACTO
            JOIN FREQUENCIA_CONTACTO fc ON c.ID_FREQUENCIA_CONTACTO = fc.ID_FREQUENCIA_CONTACTO
            WHERE c.ID_UTENTE = %s
            ORDER BY c.DATA_CONTACTO DESC
        """, [id_utente])
        contactos = cursor.fetchall()

        # 6. Quedas
        cursor.execute("""
            SELECT DATA_QUEDA, OBSERVACOES_QUEDA
            FROM QUEDAS_IDOSO
            WHERE ID_UTENTE = %s
            ORDER BY DATA_QUEDA DESC
        """, [id_utente])
        quedas = cursor.fetchall()

        # 7. Sinais de fragilidade
        cursor.execute("""
            SELECT sf.DESCRICAO_FRAGILIDADE
            FROM FRAGILIDADE_IDOSO fi
            JOIN SINAIS_FRAGILIDADE sf ON fi.ID_SINAL_FRAGILIDADE = sf.ID_SINAL_FRAGILIDADE
            WHERE fi.ID_UTENTE = %s
        """, [id_utente])
        fragilidades = cursor.fetchall()

    # Converter dados para um formato mais amigável no template
    context = {
        'utente': utente,
        'atividades': atividades,
        'doencas': doencas,
        'barreiras': barreiras,
        'contactos': contactos,
        'quedas': quedas,
        'fragilidades': fragilidades,
    }
    return render(request, 'idosos/detalhe_idoso.html', context)

# CRIAR UM UTENTE IDOSO NOVO
@login_required
def idosos_novo(request):
    if request.method == 'GET':
        context = {
            'generos': models.Genero.objects.all(),
            'zonas': models.ZonaUtente.objects.all(),
            'estados_civis': models.EstadoCivil.objects.all(),
            'graus_autonomia': models.GrauAutonomia.objects.all(),
            'mobilidades': models.Mobilidade.objects.all(),
            'niveis_isolamento': models.NivelIsolamento.objects.all(),
            'relacoes_familia': models.RelacaoFamilia.objects.all(),
            'frequencias_contacto_social': models.FrequenciaContactoSocial.objects.all(),
            'tipos_habitacao': models.TipoHabitacao.objects.all(),
            'atividades_diaria': models.AtividadesDiaria.objects.all(),
            'barreiras_arquitetonicas': models.BarreirasArquitetonicas.objects.all(),
            'doencas_cronicas': models.DoencasCronicas.objects.all(),
            'sinais_fragilidade': models.SinaisFragilidade.objects.all(),
        }
        return render(request, 'idosos/novo_idoso.html', context)

    if request.method == 'POST':
        # Recolher dados
        nome = request.POST.get('nome_utente', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '')
        id_genero = request.POST.get('genero')
        id_zona = request.POST.get('zona')
        id_estado_civil = request.POST.get('estado_civil')
        id_grau_autonomia = request.POST.get('grau_autonomia')
        id_mobilidade = request.POST.get('mobilidade')
        id_nivel_isolamento = request.POST.get('nivel_isolamento')
        id_relacao_familia = request.POST.get('relacao_familia')
        id_frequencia_contacto_social = request.POST.get('frequencia_contacto_social')
        id_tipo_habitacao = request.POST.get('tipo_habitacao')
        vive_sozinho = request.POST.get('vive_sozinho') == 'on'
        contacto_emergencia = request.POST.get('contacto_emergencia', '').strip()
        familiar_referencia = request.POST.get('familiar_referencia', '').strip()
        medicacao_diaria = request.POST.get('medicacao_diaria') == 'on'
        dificuldade_acesso_saude = request.POST.get('dificuldade_acesso_saude') == 'on'
        acompanhamento_reg = request.POST.get('acompanhamento_reg') == 'on'
        participa_atividades_fr = request.POST.get('participa_atividades_fr') == 'on'
        tristesa_depressao = request.POST.get('tristesa_depressao') == 'on'
        luto_recente = request.POST.get('luto_recente') == 'on'
        aquecimento_adeq_inv = request.POST.get('aquecimento_adeq_inv') == 'on'
        seguranca = request.POST.get('seguranca', '').strip()
        necessidade_adptacoes = request.POST.get('necessidade_adptacoes', '').strip()

        # Recolher listas das checkboxes
        doencas_ids = request.POST.getlist('doencas')
        barreiras_ids = request.POST.getlist('barreiras')
        fragilidades_ids = request.POST.getlist('fragilidades')

        # Recolher novas entradas (texto livre)
        nova_doenca = request.POST.get('nova_doenca', '').strip()
        nova_barreira = request.POST.get('nova_barreira', '').strip()
        nova_fragilidade = request.POST.get('nova_fragilidade', '').strip()

        # Validações de campos obrigatórios
        errors = []

        # Verificar duplicação de nome (case-insensitive)
        if models.Utentes.objects.filter(nome_utente__iexact=nome).exists():
            errors.append(f'Já existe um utente com o nome "{nome}". Por favor, utilize um nome diferente.')

        if not nome:
            errors.append('Nome é obrigatório.')
        if not data_nascimento:
            errors.append('Data de nascimento é obrigatória.')
        else:
            try:
                data_nasc = date.fromisoformat(data_nascimento)
                if data_nasc > date.today():
                    errors.append('Data de nascimento não pode ser futura.')
            except ValueError:
                errors.append('Data de nascimento inválida.')
        if not id_genero:
            errors.append('Sexo é obrigatório.')
        if not id_zona:
            errors.append('Zona/Freguesia é obrigatória.')
        if not id_estado_civil:
            errors.append('Estado civil é obrigatório.')
        if not id_grau_autonomia:
            errors.append('Grau de autonomia é obrigatório.')
        if not id_mobilidade:
            errors.append('Mobilidade é obrigatória.')
        if not id_nivel_isolamento:
            errors.append('Nível de isolamento é obrigatório.')
        if not id_relacao_familia:
            errors.append('Relação com a família é obrigatória.')
        if not id_frequencia_contacto_social:
            errors.append('Frequência de contacto social é obrigatória.')
        if not id_tipo_habitacao:
            errors.append('Tipo de habitação é obrigatório.')

        if errors:
            for err in errors:
                messages.error(request, err)

            return redirect('idosos_novo')

        # Processar novas entradas (criar ou obter ID)
        if nova_doenca:
            existing = models.DoencasCronicas.objects.filter(descricao_doenca_cronica__iexact=nova_doenca).first()
            if existing:
                doencas_ids.append(str(existing.id_doenca_cronica))
            else:
                nova = models.DoencasCronicas.objects.create(descricao_doenca_cronica=nova_doenca)
                doencas_ids.append(str(nova.id_doenca_cronica))

        if nova_barreira:
            existing = models.BarreirasArquitetonicas.objects.filter(descricao_barreira_arquitetonica__iexact=nova_barreira).first()
            if existing:
                barreiras_ids.append(str(existing.id_barreira_arquitetonica))
            else:
                nova = models.BarreirasArquitetonicas.objects.create(descricao_barreira_arquitetonica=nova_barreira)
                barreiras_ids.append(str(nova.id_barreira_arquitetonica))

        if nova_fragilidade:
            existing = models.SinaisFragilidade.objects.filter(descricao_fragilidade__iexact=nova_fragilidade).first()
            if existing:
                fragilidades_ids.append(str(existing.id_sinal_fragilidade))
            else:
                nova = models.SinaisFragilidade.objects.create(descricao_fragilidade=nova_fragilidade)
                fragilidades_ids.append(str(nova.id_sinal_fragilidade))

        # Se passou nas validações, criar registos
        try:
            with transaction.atomic():
                # 3.1 Criar Utentes (tipo_utente = 2 para idoso)
                utente = models.Utentes.objects.create(
                    id_tipo_utente_id=2,
                    id_genero_id=id_genero,
                    id_zona_utente_id=id_zona,
                    nome_utente=nome,
                    data_nascimento=data_nascimento,
                    data_criacao=date.today(),
                )

                # 3.2 Criar UtentesIdosos
                idoso = models.UtentesIdosos.objects.create(
                    id_utente=utente,
                    id_estado_civil_id=id_estado_civil,
                    id_grau_autonomia_id=id_grau_autonomia,
                    id_mobilidade_id=id_mobilidade,
                    id_nivel_isolamento_id=id_nivel_isolamento,
                    id_relacao_familia_id=id_relacao_familia,
                    id_frequencia_contacto_social_id=id_frequencia_contacto_social,
                    id_tipo_habitacao_id=id_tipo_habitacao,
                    vive_sozinho=vive_sozinho,
                    contacto_emergencia=contacto_emergencia,
                    familiar_referencia=familiar_referencia,
                    medicacao_diaria=medicacao_diaria,
                    dificuldade_acesso_saude=dificuldade_acesso_saude,
                    acompanhamento_reg=acompanhamento_reg,
                    participa_atividades_fr=participa_atividades_fr,
                    tristesa_depressao=tristesa_depressao,
                    luto_recente=luto_recente,
                    aquecimento_adeq_inv=aquecimento_adeq_inv,
                    seguranca=seguranca,
                    necessidade_adptacoes=necessidade_adptacoes,
                )

                # AVD
                descricao_avd = request.POST.get('descricao_avd', '').strip()
                if descricao_avd:
                    models.AtividadesDiaria.objects.create(
                        id_utente=idoso,
                        descricao_atividade_diaria=descricao_avd
                    )

                # Doenças crónicas (raw SQL)
                with connection.cursor() as cursor:
                    for did in doencas_ids:
                        if did:
                            cursor.execute(
                                "INSERT INTO doencas_idosos (id_utente, id_doenca_cronica) VALUES (%s, %s)",
                                [idoso.id_utente_id, did]
                            )

                # Barreiras arquitetónicas (raw SQL)
                with connection.cursor() as cursor:
                    for bid in barreiras_ids:
                        if bid:
                            cursor.execute(
                                "INSERT INTO barreiras_idosos (id_utente, id_barreira_arquitetonica) VALUES (%s, %s)",
                                [idoso.id_utente_id, bid]
                            )

                # Sinais de fragilidade (raw SQL)
                with connection.cursor() as cursor:
                    for fid in fragilidades_ids:
                        if fid:
                            cursor.execute(
                                "INSERT INTO fragilidade_idoso (id_utente, id_sinal_fragilidade) VALUES (%s, %s)",
                                [idoso.id_utente_id, fid]
                            )

                # QUEDAS
                datas_queda = request.POST.getlist('data_queda')
                obs_queda = request.POST.getlist('obs_queda')
                for i, data in enumerate(datas_queda):
                    if data:
                        obs = obs_queda[i].strip() if i < len(obs_queda) else ''
                        models.QuedasIdoso.objects.create(
                            id_utente=idoso,
                            data_queda=data,
                            observacoes_queda=obs
                        )

            guardar_historico_idoso(request, utente.id_utente)

            messages.success(request, f'Idoso {nome} criado com sucesso!')
            return redirect('idosos_detalhe', id_utente=utente.id_utente)

        except Exception as e:
            messages.error(request, f'Erro ao criar idoso: {str(e)}')
            # rollback automático

    return redirect('idosos_lista')


#editar um idoso atual
@login_required
def idosos_editar(request, id_utente):
    # Obter os objetos existentes
    utente = get_object_or_404(models.Utentes, pk=id_utente)
    idoso = get_object_or_404(models.UtentesIdosos, pk=id_utente)

    if request.method == 'GET':
        # Buscar dados relacionados
        avd = models.AtividadesDiaria.objects.filter(id_utente=idoso).first()
        doencas_ids = models.DoencasIdosos.objects.filter(id_utente=idoso).values_list('id_doenca_cronica_id', flat=True)
        barreiras_ids = models.BarreirasIdosos.objects.filter(id_utente=idoso).values_list('id_barreira_arquitetonica_id', flat=True)
        fragilidades_ids = models.FragilidadeIdoso.objects.filter(id_utente=idoso).values_list('id_sinal_fragilidade_id', flat=True)
        quedas = models.QuedasIdoso.objects.filter(id_utente=idoso).order_by('-data_queda')

        # Preparar dados para preencher o formulário
        submetido = {
            'nome_utente': utente.nome_utente,
            'data_nascimento': utente.data_nascimento.isoformat() if utente.data_nascimento else '',
            'genero': str(utente.id_genero_id) if utente.id_genero_id else '',
            'zona': str(utente.id_zona_utente_id) if utente.id_zona_utente_id else '',
            'estado_civil': str(idoso.id_estado_civil_id) if idoso.id_estado_civil_id else '',
            'grau_autonomia': str(idoso.id_grau_autonomia_id) if idoso.id_grau_autonomia_id else '',
            'mobilidade': str(idoso.id_mobilidade_id) if idoso.id_mobilidade_id else '',
            'nivel_isolamento': str(idoso.id_nivel_isolamento_id) if idoso.id_nivel_isolamento_id else '',
            'relacao_familia': str(idoso.id_relacao_familia_id) if idoso.id_relacao_familia_id else '',
            'frequencia_contacto_social': str(idoso.id_frequencia_contacto_social_id) if idoso.id_frequencia_contacto_social_id else '',
            'tipo_habitacao': str(idoso.id_tipo_habitacao_id) if idoso.id_tipo_habitacao_id else '',
            'vive_sozinho': idoso.vive_sozinho,
            'contacto_emergencia': idoso.contacto_emergencia or '',
            'familiar_referencia': idoso.familiar_referencia or '',
            'medicacao_diaria': idoso.medicacao_diaria,
            'dificuldade_acesso_saude': idoso.dificuldade_acesso_saude,
            'acompanhamento_reg': idoso.acompanhamento_reg,
            'participa_atividades_fr': idoso.participa_atividades_fr,
            'tristesa_depressao': idoso.tristesa_depressao,
            'luto_recente': idoso.luto_recente,
            'aquecimento_adeq_inv': idoso.aquecimento_adeq_inv,
            'seguranca': idoso.seguranca or '',
            'necessidade_adptacoes': idoso.necessidade_adptacoes or '',
            'descricao_avd': avd.descricao_atividade_diaria if avd else '',
            'doencas': [str(did) for did in doencas_ids],
            'barreiras': [str(bid) for bid in barreiras_ids],
            'fragilidades': [str(fid) for fid in fragilidades_ids],
            'quedas': [{'data': q.data_queda.isoformat() if q.data_queda else '', 'obs': q.observacoes_queda or ''} for q in quedas],
        }

        context = {
            'generos': models.Genero.objects.all(),
            'zonas': models.ZonaUtente.objects.all(),
            'estados_civis': models.EstadoCivil.objects.all(),
            'graus_autonomia': models.GrauAutonomia.objects.all(),
            'mobilidades': models.Mobilidade.objects.all(),
            'niveis_isolamento': models.NivelIsolamento.objects.all(),
            'relacoes_familia': models.RelacaoFamilia.objects.all(),
            'frequencias_contacto_social': models.FrequenciaContactoSocial.objects.all(),
            'tipos_habitacao': models.TipoHabitacao.objects.all(),
            'doencas_cronicas': models.DoencasCronicas.objects.all(),
            'barreiras_arquitetonicas': models.BarreirasArquitetonicas.objects.all(),
            'sinais_fragilidade': models.SinaisFragilidade.objects.all(),
            'submetido': submetido,
            'id_utente': id_utente,
        }
        return render(request, 'idosos/editar_idoso.html', context)

    if request.method == 'POST':
        # Recolher dados do formulário (igual à criação)
        nome = request.POST.get('nome_utente', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '')
        id_genero = request.POST.get('genero')
        id_zona = request.POST.get('zona')
        id_estado_civil = request.POST.get('estado_civil')
        id_grau_autonomia = request.POST.get('grau_autonomia')
        id_mobilidade = request.POST.get('mobilidade')
        id_nivel_isolamento = request.POST.get('nivel_isolamento')
        id_relacao_familia = request.POST.get('relacao_familia')
        id_frequencia_contacto_social = request.POST.get('frequencia_contacto_social')
        id_tipo_habitacao = request.POST.get('tipo_habitacao')
        vive_sozinho = request.POST.get('vive_sozinho') == 'on'
        contacto_emergencia = request.POST.get('contacto_emergencia', '').strip()
        familiar_referencia = request.POST.get('familiar_referencia', '').strip()
        medicacao_diaria = request.POST.get('medicacao_diaria') == 'on'
        dificuldade_acesso_saude = request.POST.get('dificuldade_acesso_saude') == 'on'
        acompanhamento_reg = request.POST.get('acompanhamento_reg') == 'on'
        participa_atividades_fr = request.POST.get('participa_atividades_fr') == 'on'
        tristesa_depressao = request.POST.get('tristesa_depressao') == 'on'
        luto_recente = request.POST.get('luto_recente') == 'on'
        aquecimento_adeq_inv = request.POST.get('aquecimento_adeq_inv') == 'on'
        seguranca = request.POST.get('seguranca', '').strip()
        necessidade_adptacoes = request.POST.get('necessidade_adptacoes', '').strip()
        descricao_avd = request.POST.get('descricao_avd', '').strip()

        # Recolher listas das checkboxes
        doencas_ids = request.POST.getlist('doencas')
        barreiras_ids = request.POST.getlist('barreiras')
        fragilidades_ids = request.POST.getlist('fragilidades')

        # Recolher novas entradas (texto livre)
        nova_doenca = request.POST.get('nova_doenca', '').strip()
        nova_barreira = request.POST.get('nova_barreira', '').strip()
        nova_fragilidade = request.POST.get('nova_fragilidade', '').strip()

        # Validações (mesmas da criação)
        errors = []
        if not nome:
            errors.append('Nome é obrigatório.')
        if not data_nascimento:
            errors.append('Data de nascimento é obrigatória.')
        else:
            try:
                data_nasc = date.fromisoformat(data_nascimento)
                if data_nasc > date.today():
                    errors.append('Data de nascimento não pode ser futura.')
            except ValueError:
                errors.append('Data de nascimento inválida.')
        if not id_genero:
            errors.append('Sexo é obrigatório.')
        if not id_zona:
            errors.append('Zona/Freguesia é obrigatória.')
        if not id_estado_civil:
            errors.append('Estado civil é obrigatório.')
        if not id_grau_autonomia:
            errors.append('Grau de autonomia é obrigatório.')
        if not id_mobilidade:
            errors.append('Mobilidade é obrigatória.')
        if not id_nivel_isolamento:
            errors.append('Nível de isolamento é obrigatório.')
        if not id_relacao_familia:
            errors.append('Relação com a família é obrigatória.')
        if not id_frequencia_contacto_social:
            errors.append('Frequência de contacto social é obrigatória.')
        if not id_tipo_habitacao:
            errors.append('Tipo de habitação é obrigatório.')

        if errors:
            for err in errors:
                messages.error(request, err)
            
            return redirect('idosos_editar', id_utente=id_utente)

        # Processar novas entradas (criar ou obter ID) – ANTES de apagar os registos existentes
        if nova_doenca:
            existing = models.DoencasCronicas.objects.filter(descricao_doenca_cronica__iexact=nova_doenca).first()
            if existing:
                doencas_ids.append(str(existing.id_doenca_cronica))
            else:
                nova = models.DoencasCronicas.objects.create(descricao_doenca_cronica=nova_doenca)
                doencas_ids.append(str(nova.id_doenca_cronica))

        if nova_barreira:
            existing = models.BarreirasArquitetonicas.objects.filter(descricao_barreira_arquitetonica__iexact=nova_barreira).first()
            if existing:
                barreiras_ids.append(str(existing.id_barreira_arquitetonica))
            else:
                nova = models.BarreirasArquitetonicas.objects.create(descricao_barreira_arquitetonica=nova_barreira)
                barreiras_ids.append(str(nova.id_barreira_arquitetonica))

        if nova_fragilidade:
            existing = models.SinaisFragilidade.objects.filter(descricao_fragilidade__iexact=nova_fragilidade).first()
            if existing:
                fragilidades_ids.append(str(existing.id_sinal_fragilidade))
            else:
                nova = models.SinaisFragilidade.objects.create(descricao_fragilidade=nova_fragilidade)
                fragilidades_ids.append(str(nova.id_sinal_fragilidade))        

        # Atualizar dados (dentro da transação)
        try:
            with transaction.atomic():
                # 1. Atualizar Utentes
                utente.nome_utente = nome
                utente.data_nascimento = data_nascimento
                utente.id_genero_id = id_genero
                utente.id_zona_utente_id = id_zona
                utente.save()

                # 2. Atualizar UtentesIdosos
                idoso.id_estado_civil_id = id_estado_civil
                idoso.id_grau_autonomia_id = id_grau_autonomia
                idoso.id_mobilidade_id = id_mobilidade
                idoso.id_nivel_isolamento_id = id_nivel_isolamento
                idoso.id_relacao_familia_id = id_relacao_familia
                idoso.id_frequencia_contacto_social_id = id_frequencia_contacto_social
                idoso.id_tipo_habitacao_id = id_tipo_habitacao
                idoso.vive_sozinho = vive_sozinho
                idoso.contacto_emergencia = contacto_emergencia
                idoso.familiar_referencia = familiar_referencia
                idoso.medicacao_diaria = medicacao_diaria
                idoso.dificuldade_acesso_saude = dificuldade_acesso_saude
                idoso.acompanhamento_reg = acompanhamento_reg
                idoso.participa_atividades_fr = participa_atividades_fr
                idoso.tristesa_depressao = tristesa_depressao
                idoso.luto_recente = luto_recente
                idoso.aquecimento_adeq_inv = aquecimento_adeq_inv
                idoso.seguranca = seguranca
                idoso.necessidade_adptacoes = necessidade_adptacoes
                idoso.save()

                # 3. AVD (como antes)
                if descricao_avd:
                    avd_obj = models.AtividadesDiaria.objects.filter(id_utente=idoso).first()
                    if avd_obj:
                        avd_obj.descricao_atividade_diaria = descricao_avd
                        avd_obj.save()
                    else:
                        models.AtividadesDiaria.objects.create(id_utente=idoso, descricao_atividade_diaria=descricao_avd)
                else:
                    models.AtividadesDiaria.objects.filter(id_utente=idoso).delete()

                # 4. Doenças – apagar e recriar (agora com os IDs incluindo a nova)
                models.DoencasIdosos.objects.filter(id_utente=idoso).delete()
                with connection.cursor() as cursor:
                    for did in doencas_ids:
                        if did:
                            cursor.execute(
                                "INSERT INTO doencas_idosos (id_utente, id_doenca_cronica) VALUES (%s, %s)",
                                [idoso.id_utente_id, did]
                            )

                # 5. Barreiras – apagar e recriar
                models.BarreirasIdosos.objects.filter(id_utente=idoso).delete()
                with connection.cursor() as cursor:
                    for bid in barreiras_ids:
                        if bid:
                            cursor.execute(
                                "INSERT INTO barreiras_idosos (id_utente, id_barreira_arquitetonica) VALUES (%s, %s)",
                                [idoso.id_utente_id, bid]
                            )

                # 6. Fragilidades – apagar e recriar
                models.FragilidadeIdoso.objects.filter(id_utente=idoso).delete()
                with connection.cursor() as cursor:
                    for fid in fragilidades_ids:
                        if fid:
                            cursor.execute(
                                "INSERT INTO fragilidade_idoso (id_utente, id_sinal_fragilidade) VALUES (%s, %s)",
                                [idoso.id_utente_id, fid]
                            )

                # 7. Quedas – apagar e recriar
                models.QuedasIdoso.objects.filter(id_utente=idoso).delete()
                datas_queda = request.POST.getlist('data_queda')
                obs_queda = request.POST.getlist('obs_queda')
                for i, data in enumerate(datas_queda):
                    if data:
                        obs = obs_queda[i].strip() if i < len(obs_queda) else ''
                        models.QuedasIdoso.objects.create(id_utente=idoso, data_queda=data, observacoes_queda=obs)

            guardar_historico_idoso(request, utente.id_utente)            

            messages.success(request, f'Idoso {nome} atualizado com sucesso!')
            return redirect('idosos_detalhe', id_utente=id_utente)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar idoso: {str(e)}')

    return redirect('idosos_lista')

@login_required
def idosos_eliminar(request, id_utente):
    # Verificar se o idoso existe
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.ID_UTENTE, u.NOME_UTENTE
            FROM UTENTES u
            JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        idoso = cursor.fetchone()
        
        if not idoso:
            messages.error(request, 'Idoso não encontrado.')
            return redirect('idosos_lista')

    # Eliminação com transação (apaga também os contactos)
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Apagar registos dependentes (ordem inversa das FK)
                cursor.execute("DELETE FROM CONTACTO WHERE ID_UTENTE = %s", [id_utente])   # ← adicionado
                cursor.execute("DELETE FROM historico_idoso WHERE id_utente = %s", [id_utente])
                cursor.execute("DELETE FROM QUEDAS_IDOSO WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM ATIVIDADES_DIARIA WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM FRAGILIDADE_IDOSO WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM BARREIRAS_IDOSOS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM DOENCAS_IDOSOS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM UTENTES_IDOSOS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM UTENTES WHERE ID_UTENTE = %s", [id_utente])
        
        messages.success(request, f'Idoso "{idoso[1]}" eliminado com sucesso.')
        return redirect('idosos_lista')
    
    except Exception as e:
        messages.error(request, f'Erro ao eliminar idoso: {str(e)}')
        return redirect('idosos_detalhe', id_utente=id_utente)