from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from ..views.historico import guardar_historico_utente
from .. import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def socioeconomicos_lista(request):
    nome_filter = request.GET.get('nome', '').strip()
    page_number = request.GET.get('page', 1)

    query = """
        SELECT 
            u.ID_UTENTE,
            u.NOME_UTENTE,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
            n.DESCRICAO_NACIONALIDADE,
            z.DESCRICAO_ZONA_UTENTE,
            sh.DESCRICAO_SITUACAO_HABITACIONAL,
            sl.DESCRICAO_SITUACAO_LABORAL,
            usec.RISCO_SOCIAL
        FROM UTENTES u
        JOIN UTENTES_SOCIO_ECONOMICAS usec ON u.ID_UTENTE = usec.ID_UTENTE
        JOIN NACIONALIDADE n ON usec.ID_NACIONALIDADE = n.ID_NACIONALIDADE
        JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
        JOIN SITUACAO_HABITACIONAL sh ON usec.ID_SITUACAO_HABITACIONAL = sh.ID_SITUACAO_HABITACIONAL
        JOIN SITUACAO_LABORAL sl ON usec.ID_SITUACAO_LABORAL = sl.ID_SITUACAO_LABORAL
    """
    params = []

    if nome_filter:
        query += " WHERE u.NOME_UTENTE ILIKE %s"
        params.append(f'%{nome_filter}%')

    query += " ORDER BY u.ID_UTENTE"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        resultados = cursor.fetchall()

    # Paginação
    paginator = Paginator(resultados, 20)  # 20 registos por página
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'socioeconomicos/lista_utentes.html', {
        'utentes': page_obj,
        'filtro_nome': nome_filter,
    })

@login_required
def socioeconomicos_detalhe(request, id_utente):
    with connection.cursor() as cursor:

        # 1 Dados principais
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
            JOIN UTENTES_SOCIO_ECONOMICAS usec 
                ON u.ID_UTENTE = usec.ID_UTENTE
            JOIN NACIONALIDADE n 
                ON usec.ID_NACIONALIDADE = n.ID_NACIONALIDADE
            JOIN ZONA_UTENTE z 
                ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            JOIN SITUACAO_HABITACIONAL sh 
                ON usec.ID_SITUACAO_HABITACIONAL = sh.ID_SITUACAO_HABITACIONAL
            JOIN SITUACAO_LABORAL sl 
                ON usec.ID_SITUACAO_LABORAL = sl.ID_SITUACAO_LABORAL
            JOIN TIPO_RENDIMENTO tr
                ON usec.ID_TIPO_RENDIMENTO = tr.ID_TIPO_RENDIMENTO
            JOIN TIPOLOGIA_AGREGADO_FAMILIAR ta
                ON usec.ID_TIPOLOGIA = ta.ID_TIPOLOGIA
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        utente = cursor.fetchone()

        if not utente:
            return render(request, '404.html', status=404)

        # 2 Intervenções
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                ti.NOME_TIPO_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                i.DATA_INTERVENCAO,
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

        # 3️⃣ Problemáticas (com período, estado e intervenção associada, se existir)
        cursor.execute("""
            SELECT 
                p.ID_PROBLEMATICA,
                p.NOME_PROBLEMATICA,
                t.DATA_INICIO,
                t.DATA_FIM,
                CASE WHEN t.DATA_FIM IS NULL THEN 'Ativa' ELSE 'Resolvida' END AS ESTADO,
                t.ID_INTERVENCAO,
                i.DATA_INTERVENCAO AS INTERV_DATA,
                ti.NOME_TIPO_INTERVENCAO AS INTERV_TIPO
            FROM TER t
            JOIN PROBLEMATICAS_IDENTIFICADAS p 
                ON t.ID_PROBLEMATICA = p.ID_PROBLEMATICA
            LEFT JOIN INTERVENCAO i ON t.ID_INTERVENCAO = i.ID_INTERVENCAO
            LEFT JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            WHERE t.ID_UTENTE = %s
            ORDER BY t.DATA_INICIO DESC
        """, [id_utente])
        problematicas = cursor.fetchall()

        # 4 Membros do agregado
        cursor.execute("""
            SELECT 
                NOME_MEMBRO,
                ANO_NASCIMENTO,
                GRAU_PARENTESCO
            FROM MEMBROS_AGREGADO_FAMILIAR
            WHERE ID_UTENTE = %s
        """, [id_utente])
        membros_agregado = cursor.fetchall()

        # 5 Despesas fixas
        cursor.execute("""
            SELECT 
                td.DESCRICAO_TIPO_DESPESA,
                df.VALOR_DESPESA
            FROM DESPESAS_FIXAS df
            JOIN TIPO_DESPESA td 
                ON df.ID_TIPO_DESPESA = td.ID_TIPO_DESPESA
            WHERE df.ID_UTENTE = %s
        """, [id_utente])
        despesas = cursor.fetchall()

        # 6 Escalão de rendimentos
        cursor.execute("""
            SELECT 
                ID_ESCALAO,
                TIPO_ESCALAO,
                VALOR_EXATO
            FROM ESCALAO_RENDIMENTOS
            WHERE ID_UTENTE = %s
            ORDER BY ID_ESCALAO DESC
        """, [id_utente])
        escaloes = cursor.fetchall()

    return render(request, 'socioeconomicos/detalhe_utente.html', {
        'utente': utente,
        'intervencoes': intervencoes,
        'problematicas': problematicas,
        'membros_agregado': membros_agregado,
        'despesas': despesas,
        'escaloes': escaloes,
    })


@login_required
def socioeconomicos_novo(request):
    # GET: prepara os dados para os dropdowns
    if request.method == 'GET':
        context = {
            'generos': models.Genero.objects.all(),
            'nacionalidades': models.Nacionalidade.objects.all(),
            'zonas': models.ZonaUtente.objects.all(),
            'tipologias': models.TipologiaAgregadoFamiliar.objects.all(),
            'situacoes_habitacionais': models.SituacaoHabitacional.objects.all(),
            'situacoes_laborais': models.SituacaoLaboral.objects.all(),
            'tipos_rendimento': models.TipoRendimento.objects.all(),
            'tipos_despesa': models.TipoDespesa.objects.all(),
            'todas_problematicas': models.ProblematicasIdentificadas.objects.all(),
        }
        return render(request, 'socioeconomicos/novo_utente.html', context)

    # POST: processa a criação
    if request.method == 'POST':
        # 1. Recolher dados do formulário
        nome = request.POST.get('nome_utente', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '')
        id_genero = request.POST.get('genero')
        id_nacionalidade = request.POST.get('nacionalidade')
        id_zona = request.POST.get('zona')
        id_tipologia = request.POST.get('tipologia')
        id_situacao_habitacional = request.POST.get('situacao_habitacional')
        id_situacao_laboral = request.POST.get('situacao_laboral')
        id_tipo_rendimento = request.POST.get('tipo_rendimento')
        risco_social_str = request.POST.get('risco_social')
        criterio_risco = request.POST.get('criterio_risco', '').strip()
        observacoes = request.POST.get('observacoes_utente', '').strip()
        problematicas_ids = request.POST.getlist('problematicas')

        # 2. Validações de campos obrigatórios
        errors = []

        # Verificar se já existe um utente com o mesmo nome (case‑insensitive)
        if models.Utentes.objects.filter(nome_utente__iexact=nome).exists():
            errors.append(f'Já existe um utente com o nome "{nome}". Por favor, utilize um nome diferente.')

        if not nome:
            errors.append('Nome é obrigatório.')
        if not data_nascimento:
            errors.append('Data de nascimento é obrigatória.')
        else:
            # verificar se data é válida e não futura
            try:
                data_nasc = date.fromisoformat(data_nascimento)
                if data_nasc > date.today():
                    errors.append('Data de nascimento não pode ser futura.')
            except ValueError:
                errors.append('Data de nascimento inválida.')
        if not id_genero:
            errors.append('Sexo é obrigatório.')
        if not id_nacionalidade:
            errors.append('Nacionalidade é obrigatória.')
        if not id_zona:
            errors.append('Zona/Freguesia é obrigatória.')
        if not id_tipologia:
            errors.append('Tipologia do agregado é obrigatória.')
        if not id_situacao_habitacional:
            errors.append('Situação habitacional é obrigatória.')
        if not id_situacao_laboral:
            errors.append('Situação laboral é obrigatória.')
        if not id_tipo_rendimento:
            errors.append('Tipo de rendimento é obrigatório.')
        if not risco_social_str:
            errors.append('Risco social é obrigatório.')
        if not problematicas_ids:
            errors.append('É necessário selecionar pelo menos uma problemática.')

        # 3. Validação de membros do agregado conforme tipologia
        #    (considerando que o utente principal não está na tabela de membros)
        nomes_membros = request.POST.getlist('nome_membro')
        anos_nasc = request.POST.getlist('ano_nascimento')
        parentescos = request.POST.getlist('grau_parentesco')
        membros_validos = []
        for i in range(len(nomes_membros)):
            if nomes_membros[i].strip():
                membros_validos.append({
                    'nome': nomes_membros[i].strip(),
                    'ano': anos_nasc[i].strip(),
                    'parentesco': parentescos[i].strip(),
                })

        if id_tipologia:
            # Buscar descrição da tipologia para verificar se é unipessoal
            try:
                tipologia_obj = models.TipologiaAgregadoFamiliar.objects.get(id_tipologia=id_tipologia)
                tipologia_desc = tipologia_obj.descricao_tipologia.lower()
            except models.TipologiaAgregadoFamiliar.DoesNotExist:
                errors.append('Tipologia selecionada inválida.')
                tipologia_desc = ''

            if tipologia_desc != 'unipessoal' and not membros_validos:
                errors.append('Para esta tipologia, é necessário adicionar pelo menos um membro do agregado familiar.')
            elif tipologia_desc == 'unipessoal' and membros_validos:
                errors.append('Para esta tipologia não deve haver outros membros do agregado familiar')

        # Se houver erros, reexibe o formulário com mensagens
        if errors:
            for err in errors:
                messages.error(request, err)
            
            return redirect('socioeconomicos_novo')

        # 4. Se tudo válido, criar registos
        risco_social = (risco_social_str == 'Em risco')

        
        try:
            with transaction.atomic():
                # 4.1 Criar Utentes (tipo_utente = 1)
                utente = models.Utentes.objects.create(
                    id_tipo_utente_id=1,   # ID fixo para socioeconómico
                    id_genero_id=id_genero,
                    id_zona_utente_id=id_zona,
                    nome_utente=nome,
                    data_nascimento=data_nascimento,
                    data_criacao=date.today(),
                )

                # 4.2 Criar UtentesSocioEconomicas
                socio = models.UtentesSocioEconomicas.objects.create(
                    id_utente=utente,
                    id_nacionalidade_id=id_nacionalidade,
                    id_tipologia_id=id_tipologia,
                    id_situacao_habitacional_id=id_situacao_habitacional,
                    id_situacao_laboral_id=id_situacao_laboral,
                    id_tipo_rendimento_id=id_tipo_rendimento,
                    risco_social=risco_social,
                    observacoes_utente=observacoes,
                    criterio_risco=criterio_risco,
                )

                # 4.3 Membros do agregado
                for membro in membros_validos:
                    models.MembrosAgregadoFamiliar.objects.create(
                        id_utente=socio,
                        nome_membro=membro['nome'],
                        ano_nascimento=int(membro['ano']) if membro['ano'] else None,
                        grau_parentesco=membro['parentesco'],
                    )

                # 4.4 Despesas fixas (se houver)
                tipos_despesa = request.POST.getlist('tipo_despesa')
                valores_despesa = request.POST.getlist('valor_despesa')
                for i in range(len(tipos_despesa)):
                    tipo_id = tipos_despesa[i]
                    valor = valores_despesa[i]
                    if tipo_id and valor:
                        models.DespesasFixas.objects.create(
                            id_tipo_despesa_id=tipo_id,
                            id_utente=socio,
                            valor_despesa=float(valor),
                        )

                # 4.5 Escalões de rendimento (se houver)
                tipos_escalao = request.POST.getlist('tipo_escalao')
                valores_escalao = request.POST.getlist('valor_exato')
                for i in range(len(tipos_escalao)):
                    tipo = tipos_escalao[i]
                    valor = valores_escalao[i]
                    if tipo and valor:
                        models.EscalaoRendimentos.objects.create(
                            id_utente=socio,
                            tipo_escalao=tipo,
                            valor_exato=float(valor),
                        )

                # 4.6 Problemáticas
                data_atual = date.today()
                nova_prob_texto = request.POST.get('nova_problematica', '').strip()
                if nova_prob_texto:
                        nova_prob = models.ProblematicasIdentificadas.objects.create(nome_problematica=nova_prob_texto)
                        novo_id = nova_prob.id_problematica
                        problematicas_ids.append(str(novo_id))

                with connection.cursor() as cursor:
                    for pid in problematicas_ids:
                        cursor.execute(
                            "INSERT INTO ter (id_utente, id_problematica, data_inicio, data_fim) VALUES (%s, %s, %s, %s)",
                            [socio.id_utente_id, pid, data_atual, None]
                        )

            guardar_historico_utente(request, utente.id_utente)

            messages.success(request, f'Utente {nome} criado com sucesso!')
            return redirect('socioeconomicos_lista')

        except Exception as e:
            messages.error(request, f'Erro ao criar utente: {str(e)}')
            # rollback automático

    # Fallback
    return redirect('socioeconomicos_lista')

@login_required
def socioeconomicos_editar(request, id_utente):
    # Obter o utente base e o registo socioeconómico
    utente = get_object_or_404(models.Utentes, pk=id_utente)
    socio = get_object_or_404(models.UtentesSocioEconomicas, pk=id_utente)

    if request.method == 'GET':
        # Preparar os dados existentes para preencher o formulário
        membros = models.MembrosAgregadoFamiliar.objects.filter(id_utente=socio).values('nome_membro', 'ano_nascimento', 'grau_parentesco')
        despesas = models.DespesasFixas.objects.filter(id_utente=socio).select_related('id_tipo_despesa').values('id_tipo_despesa_id', 'valor_despesa')
        escaloes = models.EscalaoRendimentos.objects.filter(id_utente=socio).values('tipo_escalao', 'valor_exato')
        problematicas_ids = models.Ter.objects.filter(id_utente=socio, data_fim__isnull=True).values_list('id_problematica_id', flat=True)
        # Intervenções do utente para associar à resolução
        intervencoes_utente = models.Intervencao.objects.filter(participar__id_utente=socio).order_by('-data_intervencao').distinct()

        # Montar estrutura semelhante ao 'submetido' do POST
        submetido = {
        'nome_utente': utente.nome_utente,
        'data_nascimento': utente.data_nascimento.isoformat() if utente.data_nascimento else '',
        'genero': utente.id_genero_id,
        'nacionalidade': socio.id_nacionalidade_id,
        'zona': utente.id_zona_utente_id,
        'tipologia': socio.id_tipologia_id,
        'situacao_habitacional': socio.id_situacao_habitacional_id,
        'situacao_laboral': socio.id_situacao_laboral_id,
        'tipo_rendimento': socio.id_tipo_rendimento_id,
        'risco_social': 'Em risco' if socio.risco_social else 'Situação estável',
        'criterio_risco': socio.criterio_risco or '',
        'observacoes_utente': socio.observacoes_utente or '',
        'problematicas': [str(pid) for pid in problematicas_ids],
        }

        membros_validos = [
            {'nome': m['nome_membro'], 'ano': m['ano_nascimento'], 'parentesco': m['grau_parentesco']}
            for m in membros
        ]
        despesas_validas = [
            {'tipo': d['id_tipo_despesa_id'], 'valor': d['valor_despesa']}
            for d in despesas
        ]
        escaloes_validos = [
            {'tipo': e['tipo_escalao'], 'valor': e['valor_exato']}
            for e in escaloes
        ]

        context = {
            'generos': models.Genero.objects.all(),
            'nacionalidades': models.Nacionalidade.objects.all(),
            'zonas': models.ZonaUtente.objects.all(),
            'tipologias': models.TipologiaAgregadoFamiliar.objects.all(),
            'situacoes_habitacionais': models.SituacaoHabitacional.objects.all(),
            'situacoes_laborais': models.SituacaoLaboral.objects.all(),
            'tipos_rendimento': models.TipoRendimento.objects.all(),
            'tipos_despesa': models.TipoDespesa.objects.all(),
            'todas_problematicas': models.ProblematicasIdentificadas.objects.all(),
            'submetido': submetido,
            'membros_submetidos': membros_validos,
            'despesas_submetidas': despesas_validas,
            'escaloes_submetidos': escaloes_validos,
            'intervencoes_utente': intervencoes_utente,
            'id_utente': id_utente,
        }
        return render(request, 'socioeconomicos/editar_utente.html', context)

    # POST – atualizar dados
    if request.method == 'POST':
        # Recolher dados do formulário (igual à criação)
        nome = request.POST.get('nome_utente', '').strip()
        data_nascimento = request.POST.get('data_nascimento', '')
        id_genero = request.POST.get('genero')
        id_nacionalidade = request.POST.get('nacionalidade')
        id_zona = request.POST.get('zona')
        id_tipologia = request.POST.get('tipologia')
        id_situacao_habitacional = request.POST.get('situacao_habitacional')
        id_situacao_laboral = request.POST.get('situacao_laboral')
        id_tipo_rendimento = request.POST.get('tipo_rendimento')
        risco_social_str = request.POST.get('risco_social')
        criterio_risco = request.POST.get('criterio_risco', '').strip()
        observacoes = request.POST.get('observacoes_utente', '').strip()
        problematicas_ids = request.POST.getlist('problematicas')

        # Validações (reaproveitar lógica da criação)
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
        if not id_nacionalidade:
            errors.append('Nacionalidade é obrigatória.')
        if not id_zona:
            errors.append('Zona/Freguesia é obrigatória.')
        if not id_tipologia:
            errors.append('Tipologia do agregado é obrigatória.')
        if not id_situacao_habitacional:
            errors.append('Situação habitacional é obrigatória.')
        if not id_situacao_laboral:
            errors.append('Situação laboral é obrigatória.')
        if not id_tipo_rendimento:
            errors.append('Tipo de rendimento é obrigatório.')
        if not risco_social_str:
            errors.append('Risco social é obrigatório.')

        resolucoes = {}
        for key, value in request.POST.items():
            if key.startswith('resolucao_intervencao_') and value:
                pid = key.split('_')[-1]
                resolucoes[pid] = value

        # Membros
        nomes_membros = request.POST.getlist('nome_membro')
        anos_nasc = request.POST.getlist('ano_nascimento')
        parentescos = request.POST.getlist('grau_parentesco')
        membros_validos = []
        for i in range(len(nomes_membros)):
            if nomes_membros[i].strip():
                membros_validos.append({
                    'nome': nomes_membros[i].strip(),
                    'ano': anos_nasc[i].strip(),
                    'parentesco': parentescos[i].strip(),
                })

        if id_tipologia:
            try:
                tipologia_obj = models.TipologiaAgregadoFamiliar.objects.get(id_tipologia=id_tipologia)
                tipologia_desc = tipologia_obj.descricao_tipologia.lower()
            except models.TipologiaAgregadoFamiliar.DoesNotExist:
                errors.append('Tipologia selecionada inválida.')
                tipologia_desc = ''
            if tipologia_desc != 'unipessoal' and not membros_validos:
                errors.append('Para esta tipologia, é necessário adicionar pelo menos um membro do agregado familiar.')
            elif tipologia_desc == 'unipessoal' and membros_validos:
                errors.append('Para esta tipologia não deve haver outros membros do agregado familiar')

        if errors:
            for err in errors:
                messages.error(request, err)
            # Redirecionar para a página de edição (GET)
            return redirect('socioeconomicos_editar', id_utente=id_utente)

        # Se passou nas validações, atualizar

        risco_social = (risco_social_str == 'Em risco')
        try:
            with transaction.atomic():
                # 1. Atualizar dados básicos do utente
                utente.nome_utente = nome
                utente.data_nascimento = data_nascimento
                utente.id_genero_id = id_genero
                utente.id_zona_utente_id = id_zona
                utente.save()

                # 2. Atualizar dados socioeconómicos
                socio.id_nacionalidade_id = id_nacionalidade
                socio.id_tipologia_id = id_tipologia
                socio.id_situacao_habitacional_id = id_situacao_habitacional
                socio.id_situacao_laboral_id = id_situacao_laboral
                socio.id_tipo_rendimento_id = id_tipo_rendimento
                socio.risco_social = risco_social
                socio.criterio_risco = criterio_risco
                socio.observacoes_utente = observacoes
                socio.save()

                # 3. Membros – apagar todos e recriar (simples)
                models.MembrosAgregadoFamiliar.objects.filter(id_utente=socio).delete()
                for m in membros_validos:
                    models.MembrosAgregadoFamiliar.objects.create(
                        id_utente=socio,
                        nome_membro=m['nome'],
                        ano_nascimento=int(m['ano']) if m['ano'] else None,
                        grau_parentesco=m['parentesco'],
                    )

                # 4. Despesas fixas – apagar e recriar
                models.DespesasFixas.objects.filter(id_utente=socio).delete()
                tipos_despesa = request.POST.getlist('tipo_despesa')
                valores_despesa = request.POST.getlist('valor_despesa')
                for i in range(len(tipos_despesa)):
                    tipo_id = tipos_despesa[i]
                    valor = valores_despesa[i]
                    if tipo_id and valor:
                        models.DespesasFixas.objects.create(
                            id_tipo_despesa_id=tipo_id,
                            id_utente=socio,
                            valor_despesa=float(valor),
                        )

                # 5. Escalões – apagar e recriar
                models.EscalaoRendimentos.objects.filter(id_utente=socio).delete()
                tipos_escalao = request.POST.getlist('tipo_escalao')
                valores_escalao = request.POST.getlist('valor_exato')
                for i in range(len(tipos_escalao)):
                    tipo = tipos_escalao[i]
                    valor = valores_escalao[i]
                    if tipo and valor:
                        models.EscalaoRendimentos.objects.create(
                            id_utente=socio,
                            tipo_escalao=tipo,
                            valor_exato=float(valor),
                        )

                # 6. Problemáticas – atualizar com datas

                # Campo aberto: nova problemática (opcional, sem separadores)
                nova_prob_texto = request.POST.get('nova_problematica', '').strip()
                if nova_prob_texto:
                        nova_prob = models.ProblematicasIdentificadas.objects.create(nome_problematica=nova_prob_texto)
                        novo_id = nova_prob.id_problematica
                        problematicas_ids.append(str(novo_id))

                # 4. Problemáticas – atualizar com datas e associação a intervenção
                # Obter IDs das problemáticas atualmente ativas
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id_problematica FROM ter WHERE id_utente = %s AND data_fim IS NULL",
                        [socio.id_utente_id]
                    )
                    atuais = {row[0] for row in cursor.fetchall()}

                novas = set(int(pid) for pid in problematicas_ids)
                removidas = atuais - novas
                adicionadas = novas - atuais

                # Resolver as removidas: data_fim = hoje, e opcionalmente id_intervencao
                if removidas:
                    with connection.cursor() as cursor:
                        for pid in removidas:
                            id_interv = resolucoes.get(str(pid))
                            cursor.execute(
                                "UPDATE ter SET data_fim = %s, id_intervencao = %s WHERE id_utente = %s AND id_problematica = %s AND data_fim IS NULL",
                                [date.today(), id_interv if id_interv else None, socio.id_utente_id, pid]
                            )

                # Adicionar novas problemáticas (data_inicio = hoje)
                if adicionadas:
                    with connection.cursor() as cursor:
                        for pid in adicionadas:
                            cursor.execute(
                                "INSERT INTO ter (id_utente, id_problematica, data_inicio, data_fim, id_intervencao) VALUES (%s, %s, %s, %s, %s)",
                                [socio.id_utente_id, pid, date.today(), None, None]
                            )

            guardar_historico_utente(request, utente.id_utente)

            messages.success(request, f'Utente {nome} atualizado com sucesso!')
            return redirect('socioeconomicos_detalhe', id_utente=id_utente)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar utente: {str(e)}')

    return redirect('socioeconomicos_lista')

@login_required
def socioeconomicos_eliminar(request, id_utente):
    with connection.cursor() as cursor:
        cursor.execute("SELECT ID_UTENTE, NOME_UTENTE FROM UTENTES WHERE ID_UTENTE = %s", [id_utente])
        utente = cursor.fetchone()
        if not utente:
            messages.error(request, 'Utente não encontrado.')
            return redirect('socioeconomicos_lista')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # 1. Identificar as intervenções em que o utente participa
                cursor.execute("""
                    SELECT DISTINCT ID_INTERVENCAO
                    FROM PARTICIPAR
                    WHERE ID_UTENTE = %s
                """, [id_utente])
                intervencoes_afetadas = [row[0] for row in cursor.fetchall()]

                # 2. Remover o utente de todas as participações
                cursor.execute("DELETE FROM PARTICIPAR WHERE ID_UTENTE = %s", [id_utente])

                # 3. Para cada intervenção que ficou sem participantes, eliminar os encaminhamentos e depois a intervenção
                for id_interv in intervencoes_afetadas:
                    # Verificar se ainda restam participantes nessa intervenção
                    cursor.execute("SELECT COUNT(*) FROM PARTICIPAR WHERE ID_INTERVENCAO = %s", [id_interv])
                    count = cursor.fetchone()[0]
                    if count == 0:
                        # Apagar encaminhamentos associados a esta intervenção
                        cursor.execute("DELETE FROM ENCAMINHAMENTOS_REDE WHERE ID_INTERVENCAO = %s", [id_interv])
                        # Apagar a intervenção
                        cursor.execute("DELETE FROM INTERVENCAO WHERE ID_INTERVENCAO = %s", [id_interv])

                # 4. Apagar os restantes dados do utente (ordem inversa das FK)
                cursor.execute("DELETE FROM HISTORICO_UTENTE_SOCIOECONOMICO WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM TER WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM MEMBROS_AGREGADO_FAMILIAR WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM DESPESAS_FIXAS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM ESCALAO_RENDIMENTOS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM UTENTES_SOCIO_ECONOMICAS WHERE ID_UTENTE = %s", [id_utente])
                cursor.execute("DELETE FROM UTENTES WHERE ID_UTENTE = %s", [id_utente])

        messages.success(request, f'Utente "{utente[1]}" eliminado com sucesso. Intervenções sem participantes também foram removidas.')

    except Exception as e:
        messages.error(request, f'Erro ao eliminar utente: {str(e)}')
        return redirect('socioeconomicos_detalhe', id_utente=id_utente)

    return redirect('socioeconomicos_lista')