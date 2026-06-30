from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from .. import models
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def encaminhamentos_lista(request):
    page_number = request.GET.get('page', 1)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.ID_ENCAMINHAMENTO,
                e.DATA_RESPOSTA,
                ent.NOME_ENTIDADE,
                tr.DESCRICAO_TIPO_RESPOSTA,
                e.ENCAMINHAMENTO_FEITO,
                e.TEMPO_RESPOSTA,
                e.DESCRICAO_ENCAMINHAMENTO,
                i.ID_INTERVENCAO
            FROM ENCAMINHAMENTOS_REDE e
            JOIN ENTIDADE ent ON e.ID_ENTIDADE = ent.ID_ENTIDADE
            JOIN TIPO_RESPOSTA tr ON e.ID_TIPO_RESPOSTA = tr.ID_TIPO_RESPOSTA
            JOIN INTERVENCAO i ON e.ID_INTERVENCAO = i.ID_INTERVENCAO
            ORDER BY e.DATA_RESPOSTA DESC NULLS LAST
        """)
        todos_encaminhamentos = cursor.fetchall()

    paginator = Paginator(todos_encaminhamentos, 20)  # 20 por página
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'encaminhamentos/lista_encaminhamentos.html', {
        'encaminhamentos': page_obj,
    })

@login_required
def encaminhamentos_detalhe(request, id):
    with connection.cursor() as cursor:
        # 1. Dados principais do encaminhamento + intervenção associada
        cursor.execute("""
            SELECT 
                e.ID_ENCAMINHAMENTO,
                e.DESCRICAO_ENCAMINHAMENTO,
                e.ENCAMINHAMENTO_FEITO,
                e.DATA_RESPOSTA,
                e.TEMPO_RESPOSTA,
                e.OBSERVACOES_ENCAMINHAMENTO,
                ent.NOME_ENTIDADE,
                tr.DESCRICAO_TIPO_RESPOSTA,
                i.ID_INTERVENCAO,
                i.DATA_INTERVENCAO,
                ti.NOME_TIPO_INTERVENCAO,
                p.PROGRAMA,
                a.NOME_ADMINISTRADOR
            FROM ENCAMINHAMENTOS_REDE e
            JOIN INTERVENCAO i ON e.ID_INTERVENCAO = i.ID_INTERVENCAO
            JOIN ENTIDADE ent ON e.ID_ENTIDADE = ent.ID_ENTIDADE
            LEFT JOIN TIPO_RESPOSTA tr ON e.ID_TIPO_RESPOSTA = tr.ID_TIPO_RESPOSTA
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            JOIN ADMINISTRADORES a ON i.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            WHERE e.ID_ENCAMINHAMENTO = %s
        """, [id])
        encaminhamento = cursor.fetchone()

        if not encaminhamento:
            messages.error(request, 'Encaminhamento não encontrado.')
            return redirect('encaminhamentos_lista')

        # 2. Utentes participantes na intervenção associada
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
        """, [encaminhamento[8]])  # encaminhamento[8] é ID_INTERVENCAO
        utentes = cursor.fetchall()

    return render(request, 'encaminhamentos/detalhe_encaminhamento.html', {
        'enc': encaminhamento,
        'utentes': utentes,
    })

@login_required
def encaminhamentos_novo(request):
    if request.method == 'GET':
        context = {
            'intervencoes': models.Intervencao.objects.select_related(
                'id_tipo_intervencao', 'id_entidade', 'id_programa'
            ).order_by('-data_intervencao'),
            'entidades': models.Entidade.objects.all(),
            'tipos_resposta': models.TipoResposta.objects.all(),
        }
        return render(request, 'encaminhamentos/novo_encaminhamento.html', context)

    if request.method == 'POST':
        # Recolher dados
        id_intervencao = request.POST.get('intervencao')  # radio button value
        id_entidade = request.POST.get('entidade')
        id_tipo_resposta = request.POST.get('tipo_resposta')
        descricao = request.POST.get('descricao', '').strip()
        encaminhamento_feito = request.POST.get('encaminhamento_feito') == 'on'
        data_resposta = request.POST.get('data_resposta')
        tempo_resposta = request.POST.get('tempo_resposta')
        observacoes = request.POST.get('observacoes', '').strip()

        # Validações
        errors = []
        if not id_intervencao:
            errors.append('É necessário selecionar uma intervenção.')
        if not id_entidade:
            errors.append('A entidade é obrigatória.')
        if not descricao:
            errors.append('A descrição do encaminhamento é obrigatória.')

        if errors:
            for err in errors:
                messages.error(request, err)
            
            return redirect('encaminhamentos_novo')

        try:
            with transaction.atomic():
                encaminhamento = models.EncaminhamentosRede.objects.create(
                    id_intervencao_id=id_intervencao,
                    id_entidade_id=id_entidade,
                    id_tipo_resposta_id=id_tipo_resposta if id_tipo_resposta else None,
                    descricao_encaminhamento=descricao,
                    encaminhamento_feito=encaminhamento_feito,
                    data_resposta=data_resposta if data_resposta else None,
                    tempo_resposta=int(tempo_resposta) if tempo_resposta else None,
                    observacoes_encaminhamento=observacoes,
                )
            messages.success(request, f'Encaminhamento #{encaminhamento.id_encaminhamento} criado com sucesso!')
            return redirect('encaminhamentos_detalhe', id=encaminhamento.id_encaminhamento)

        except Exception as e:
            messages.error(request, f'Erro ao criar encaminhamento: {str(e)}')

    return redirect('encaminhamentos_lista')

@login_required
def encaminhamentos_editar(request, id):
    encaminhamento = get_object_or_404(models.EncaminhamentosRede, pk=id)

    if request.method == 'GET':
        # Obter a descrição textual da intervenção atual (para pré‑seleção no Select2)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    i.ID_INTERVENCAO,
                    to_char(i.DATA_INTERVENCAO, 'DD/MM/YYYY HH24:MI') as DATA,
                    ti.NOME_TIPO_INTERVENCAO,
                    e.NOME_ENTIDADE,
                    p.PROGRAMA
                FROM INTERVENCAO i
                JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
                JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
                JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
                WHERE i.ID_INTERVENCAO = %s
            """, [encaminhamento.id_intervencao_id])
            row = cursor.fetchone()
            if row:
                intervencao_atual_text = f"#{row[0]} - {row[1]} - {row[2]} ({row[3]} / {row[4]})"
            else:
                intervencao_atual_text = ""

        context = {
            'encaminhamento': encaminhamento,
            'intervencoes': models.Intervencao.objects.select_related(
                'id_tipo_intervencao', 'id_entidade', 'id_programa'
            ).order_by('-data_intervencao'),
            'entidades': models.Entidade.objects.all(),
            'tipos_resposta': models.TipoResposta.objects.all(),
            'intervencao_atual_text': intervencao_atual_text,   # para pré‑seleção
            'intervencao_atual_id': encaminhamento.id_intervencao_id,
        }
        return render(request, 'encaminhamentos/editar_encaminhamento.html', context)

    if request.method == 'POST':
        # Recolher dados
        id_intervencao = request.POST.get('intervencao')
        id_entidade = request.POST.get('entidade')
        id_tipo_resposta = request.POST.get('tipo_resposta')
        descricao = request.POST.get('descricao', '').strip()
        encaminhamento_feito = request.POST.get('encaminhamento_feito') == 'on'
        data_resposta = request.POST.get('data_resposta')
        tempo_resposta = request.POST.get('tempo_resposta')
        observacoes = request.POST.get('observacoes', '').strip()

        # Validações (idênticas à criação)
        errors = []
        if not id_intervencao:
            errors.append('É necessário selecionar uma intervenção.')
        if not id_entidade:
            errors.append('A entidade é obrigatória.')
        if not descricao:
            errors.append('A descrição do encaminhamento é obrigatória.')

        if errors:
            for err in errors:
                messages.error(request, err)

            return redirect('encaminhamentos_editar', id=id)

        try:
            with transaction.atomic():
                encaminhamento.id_intervencao_id = id_intervencao
                encaminhamento.id_entidade_id = id_entidade
                encaminhamento.id_tipo_resposta_id = id_tipo_resposta if id_tipo_resposta else None
                encaminhamento.descricao_encaminhamento = descricao
                encaminhamento.encaminhamento_feito = encaminhamento_feito
                encaminhamento.data_resposta = data_resposta if data_resposta else None
                encaminhamento.tempo_resposta = int(tempo_resposta) if tempo_resposta else None
                encaminhamento.observacoes_encaminhamento = observacoes
                encaminhamento.save()

            messages.success(request, f'Encaminhamento #{encaminhamento.id_encaminhamento} atualizado com sucesso!')
            return redirect('encaminhamentos_detalhe', id=encaminhamento.id_encaminhamento)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar encaminhamento: {str(e)}')

    return redirect('encaminhamentos_lista')

@login_required
def encaminhamentos_eliminar(request, id):
    # Verificar se o encaminhamento existe
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ID_ENCAMINHAMENTO FROM ENCAMINHAMENTOS_REDE WHERE ID_ENCAMINHAMENTO = %s",
            [id]
        )
        if not cursor.fetchone():
            messages.error(request, 'Encaminhamento não encontrado.')
            return redirect('encaminhamentos_lista')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM ENCAMINHAMENTOS_REDE WHERE ID_ENCAMINHAMENTO = %s",
                    [id]
                )
        messages.success(request, f'Encaminhamento #{id} eliminado com sucesso.')
    except Exception as e:
        messages.error(request, f'Erro ao eliminar encaminhamento: {str(e)}')

    return redirect('encaminhamentos_lista')


@login_required
def intervencoes_autocomplete(request):
    termo = request.GET.get('q', '')
    if len(termo) < 2:
        return JsonResponse({'results': []})
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                to_char(i.DATA_INTERVENCAO, 'DD/MM/YYYY HH24:MI') as DATA,
                ti.NOME_TIPO_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                a.NOME_ADMINISTRADOR
            FROM INTERVENCAO i
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            JOIN ADMINISTRADORES a ON i.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            WHERE CAST(i.ID_INTERVENCAO AS TEXT) ILIKE %s
               OR ti.NOME_TIPO_INTERVENCAO ILIKE %s
               OR e.NOME_ENTIDADE ILIKE %s
               OR p.PROGRAMA ILIKE %s
            ORDER BY i.DATA_INTERVENCAO DESC
            LIMIT 20
        """, [f'%{termo}%', f'%{termo}%', f'%{termo}%', f'%{termo}%'])
        resultados = cursor.fetchall()
    
    results = [
        {
            'id': row[0],
            'text': f"#{row[0]} - {row[1]} - {row[2]} ({row[3]} / {row[4]})"
        }
        for row in resultados
    ]
    return JsonResponse({'results': results})