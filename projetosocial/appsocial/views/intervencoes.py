from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from .. import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#Listar Intervencoes

@login_required
def intervencoes_lista(request):
    # Obter o número da página (padrão = 1)
    page_number = request.GET.get('page', 1)

    # Query SQL (sem alterações)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                i.DATA_INTERVENCAO,
                ti.NOME_TIPO_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                a.NOME_ADMINISTRADOR,
                (SELECT COUNT(*) FROM PARTICIPAR WHERE ID_INTERVENCAO = i.ID_INTERVENCAO) AS NUM_UTENTES
            FROM INTERVENCAO i
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            JOIN ADMINISTRADORES a ON i.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            ORDER BY i.DATA_INTERVENCAO DESC
        """)
        todas_intervencoes = cursor.fetchall()

    # Paginação (50 itens por página, por exemplo)
    paginator = Paginator(todas_intervencoes, 20)  # ajuste o número conforme necessário
    try:
        intervencoes_page = paginator.page(page_number)
    except PageNotAnInteger:
        intervencoes_page = paginator.page(1)
    except EmptyPage:
        intervencoes_page = paginator.page(paginator.num_pages)

    return render(request, 'intervencoes/lista_intervencoes.html', {
        'intervencoes': intervencoes_page,
    })

@login_required
def criar_intervencao(request):
    if request.method == 'GET':
        context = {
            'tipos_intervencao': models.TipoIntervencao.objects.all(),
            'entidades': models.Entidade.objects.all(),
            'programas': models.Programa.objects.all(),
            'utentes': models.UtentesSocioEconomicas.objects.select_related('id_utente').all(),
        }
        return render(request, 'intervencoes/criar_intervencao.html', context)

    if request.method == 'POST':
        # Recolher dados do formulário
        id_tipo = request.POST.get('tipo_intervencao')
        id_entidade = request.POST.get('entidade')
        id_programa = request.POST.get('programa')
        data_intervencao = request.POST.get('data_intervencao')
        observacoes = request.POST.get('observacoes', '').strip()
        utentes_ids = request.POST.getlist('utentes')

        # Campos de texto livre (apenas para recolher, não criar agora)
        novo_tipo = request.POST.get('novo_tipo_intervencao', '').strip()
        nova_entidade = request.POST.get('nova_entidade', '').strip()
        novo_programa = request.POST.get('novo_programa', '').strip()

        # Validações (sem criar ainda)
        errors = []
        if not data_intervencao:
            errors.append('Data da intervenção é obrigatória.')
        if not utentes_ids:
            errors.append('É necessário selecionar pelo menos um utente.')

        # Se não houver tipo/entidade/programa nem novo texto, erro
        if not id_tipo and not novo_tipo:
            errors.append('Tipo de intervenção é obrigatório.')
        if not id_entidade and not nova_entidade:
            errors.append('Entidade é obrigatória.')
        if not id_programa and not novo_programa:
            errors.append('Programa é obrigatório.')

        if errors:
            for err in errors:
                messages.error(request, err)

            return redirect('criar_intervencao')

        # Obter ID do administrador
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ID_ADMINISTRADOR FROM ADMINISTRADORES WHERE EMAIL_ADMINISTRADOR = %s",
                [request.user.email]
            )
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Utilizador não está registado como administrador.')
                return redirect('intervencoes_lista')
            id_administrador = row[0]

        try:
            with transaction.atomic():
                # 1. Criar novo tipo de intervenção se foi fornecido texto
                if novo_tipo:
                    novo_obj = models.TipoIntervencao.objects.create(nome_tipo_intervencao=novo_tipo)
                    id_tipo = novo_obj.id_tipo_intervencao
                # 2. Criar nova entidade se foi fornecido texto
                if nova_entidade:
                    novo_obj = models.Entidade.objects.create(nome_entidade=nova_entidade)
                    id_entidade = novo_obj.id_entidade
                # 3. Criar novo programa se foi fornecido texto
                if novo_programa:
                    novo_obj = models.Programa.objects.create(programa=novo_programa)
                    id_programa = novo_obj.id_programa

                # 4. Criar intervenção
                intervencao = models.Intervencao.objects.create(
                    id_administrador_id=id_administrador,
                    id_tipo_intervencao_id=id_tipo,
                    id_entidade_id=id_entidade,
                    id_programa_id=id_programa,
                    data_intervencao=data_intervencao,
                    observacoes_intervencao=observacoes,
                )

                # 5. Associar utentes
                with connection.cursor() as cursor:
                    for uid in utentes_ids:
                        cursor.execute(
                            "INSERT INTO participar (id_utente, id_intervencao) VALUES (%s, %s)",
                            [uid, intervencao.id_intervencao]
                        )

            messages.success(request, f'Intervenção #{intervencao.id_intervencao} criada com sucesso!')
            return redirect('detalhe_intervencao', id=intervencao.id_intervencao)

        except Exception as e:
            messages.error(request, f'Erro ao criar intervenção: {str(e)}')

    return redirect('intervencoes_lista')

@login_required
def detalhe_intervencao(request, id):
    with connection.cursor() as cursor:
        # Dados principais da intervenção (já existente)
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                a.NOME_ADMINISTRADOR,
                ti.NOME_TIPO_INTERVENCAO,
                i.DATA_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                i.OBSERVACOES_INTERVENCAO,
                (SELECT COUNT(*) FROM PARTICIPAR WHERE ID_INTERVENCAO = i.ID_INTERVENCAO) AS NUM_UTENTES
            FROM INTERVENCAO i
            JOIN ADMINISTRADORES a ON i.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            WHERE i.ID_INTERVENCAO = %s
        """, [id])
        intervencao = cursor.fetchone()

        if not intervencao:
            return redirect("intervencoes_lista")

        # Utentes participantes (já existente)
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS IDADE,
                g.DESCRICAO_GENERO AS SEXO,
                z.DESCRICAO_ZONA_UTENTE AS ZONA,
                se.RISCO_SOCIAL
            FROM PARTICIPAR p
            JOIN UTENTES_SOCIO_ECONOMICAS se ON p.ID_UTENTE = se.ID_UTENTE
            JOIN UTENTES u ON se.ID_UTENTE = u.ID_UTENTE
            JOIN GENERO g ON u.ID_GENERO = g.ID_GENERO
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            WHERE p.ID_INTERVENCAO = %s
            ORDER BY u.NOME_UTENTE
        """, [id])
        utentes = cursor.fetchall()

        # --- NOVO: Encaminhamentos associados ---
        cursor.execute("""
            SELECT 
                e.ID_ENCAMINHAMENTO,
                ent.NOME_ENTIDADE,
                tr.DESCRICAO_TIPO_RESPOSTA,
                e.ENCAMINHAMENTO_FEITO,
                e.DATA_RESPOSTA,
                e.TEMPO_RESPOSTA,
                e.DESCRICAO_ENCAMINHAMENTO,
                e.OBSERVACOES_ENCAMINHAMENTO
            FROM ENCAMINHAMENTOS_REDE e
            JOIN ENTIDADE ent ON e.ID_ENTIDADE = ent.ID_ENTIDADE
            LEFT JOIN TIPO_RESPOSTA tr ON e.ID_TIPO_RESPOSTA = tr.ID_TIPO_RESPOSTA
            WHERE e.ID_INTERVENCAO = %s
            ORDER BY e.DATA_RESPOSTA DESC NULLS LAST
        """, [id])
        encaminhamentos = cursor.fetchall()

    return render(request, "intervencoes/detalhe_intervencao.html", {
        "intervencao": intervencao,
        "utentes": utentes,
        "encaminhamentos": encaminhamentos,   # nova variável
    })

@login_required
def editar_intervencao(request, id):
    intervencao = get_object_or_404(models.Intervencao, pk=id)

    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("SELECT ID_UTENTE FROM PARTICIPAR WHERE ID_INTERVENCAO = %s", [id])
            utentes_associados = [str(row[0]) for row in cursor.fetchall()]

        submetido = {
            'tipo_intervencao': str(intervencao.id_tipo_intervencao_id) if intervencao.id_tipo_intervencao_id else '',
            'entidade': str(intervencao.id_entidade_id) if intervencao.id_entidade_id else '',
            'programa': str(intervencao.id_programa_id) if intervencao.id_programa_id else '',
            'data_intervencao': intervencao.data_intervencao.isoformat() if intervencao.data_intervencao else '',
            'observacoes': intervencao.observacoes_intervencao or '',
            'utentes': utentes_associados,
        }

        context = {
            'intervencao': intervencao,
            'tipos_intervencao': models.TipoIntervencao.objects.all(),
            'entidades': models.Entidade.objects.all(),
            'programas': models.Programa.objects.all(),
            'utentes': models.UtentesSocioEconomicas.objects.select_related('id_utente').all(),
            'utentes_associados': utentes_associados,
            'submetido': submetido,
        }
        return render(request, 'intervencoes/editar_intervencao.html', context)

    if request.method == 'POST':
        # Recolher dados do formulário
        id_tipo = request.POST.get('tipo_intervencao')
        id_entidade = request.POST.get('entidade')
        id_programa = request.POST.get('programa')
        data_intervencao = request.POST.get('data_intervencao')
        observacoes = request.POST.get('observacoes', '').strip()
        utentes_ids = request.POST.getlist('utentes')

        # Campos de texto livre (apenas para recolher)
        novo_tipo = request.POST.get('novo_tipo_intervencao', '').strip()
        nova_entidade = request.POST.get('nova_entidade', '').strip()
        novo_programa = request.POST.get('novo_programa', '').strip()

        # Validações (sem criar ainda)
        errors = []
        if not data_intervencao:
            errors.append('Data da intervenção é obrigatória.')
        if not utentes_ids:
            errors.append('É necessário selecionar pelo menos um utente.')

        if not id_tipo and not novo_tipo:
            errors.append('Tipo de intervenção é obrigatório.')
        if not id_entidade and not nova_entidade:
            errors.append('Entidade é obrigatória.')
        if not id_programa and not novo_programa:
            errors.append('Programa é obrigatório.')

        if errors:
            for err in errors:
                messages.error(request, err)
            
            return redirect('editar_intervencao', id=id)

        try:
            with transaction.atomic():
                # Criar novo tipo se fornecido (substitui o dropdown)
                if novo_tipo:
                    novo_obj = models.TipoIntervencao.objects.create(nome_tipo_intervencao=novo_tipo)
                    id_tipo = novo_obj.id_tipo_intervencao
                if nova_entidade:
                    novo_obj = models.Entidade.objects.create(nome_entidade=nova_entidade)
                    id_entidade = novo_obj.id_entidade
                if novo_programa:
                    novo_obj = models.Programa.objects.create(programa=novo_programa)
                    id_programa = novo_obj.id_programa

                # Atualizar intervenção
                intervencao.id_tipo_intervencao_id = id_tipo
                intervencao.id_entidade_id = id_entidade
                intervencao.id_programa_id = id_programa
                intervencao.data_intervencao = data_intervencao
                intervencao.observacoes_intervencao = observacoes
                intervencao.save()

                # Atualizar utentes participantes
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM PARTICIPAR WHERE ID_INTERVENCAO = %s", [id])
                    for uid in utentes_ids:
                        cursor.execute(
                            "INSERT INTO PARTICIPAR (id_utente, id_intervencao) VALUES (%s, %s)",
                            [uid, id]
                        )

            messages.success(request, f'Intervenção #{id} atualizada com sucesso!')
            return redirect('detalhe_intervencao', id=id)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar intervenção: {str(e)}')

    return redirect('intervencoes_lista')

@login_required
def eliminar_intervencao(request, id):
    # Verificar se a intervenção existe
    with connection.cursor() as cursor:
        cursor.execute("SELECT ID_INTERVENCAO FROM INTERVENCAO WHERE ID_INTERVENCAO = %s", [id])
        if not cursor.fetchone():
            messages.error(request, 'Intervenção não encontrada.')
            return redirect('intervencoes_lista')

        # Verificar se existem encaminhamentos associados
        cursor.execute("SELECT COUNT(*) FROM ENCAMINHAMENTOS_REDE WHERE ID_INTERVENCAO = %s", [id])
        count = cursor.fetchone()[0]
        if count > 0:
            messages.error(
                request,
                f'Não é possível eliminar a intervenção #{id} porque existem {count} encaminhamento(s) associado(s).'
            )
            return redirect('intervencoes_lista')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Apagar registos em PARTICIPAR
                cursor.execute("DELETE FROM PARTICIPAR WHERE ID_INTERVENCAO = %s", [id])
                # Apagar a intervenção
                cursor.execute("DELETE FROM INTERVENCAO WHERE ID_INTERVENCAO = %s", [id])

        messages.success(request, f'Intervenção #{id} eliminada com sucesso.')
        return redirect('intervencoes_lista')

    except Exception as e:
        messages.error(request, f'Erro ao eliminar intervenção: {str(e)}')
        return redirect('intervencoes_lista')