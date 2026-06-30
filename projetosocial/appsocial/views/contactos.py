from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .. import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def listar_contactos(request):
    page_number = request.GET.get('page', 1)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.ID_CONTACTO,
                u.NOME_UTENTE AS NOME_IDOSO,
                tc.NOME_TIPO_CONTACTO AS TIPO_CONTACTO,
                c.DATA_CONTACTO,
                fc.DESCRICAO_FREQUENCIA_CONTACTO AS FREQUENCIA,
                c.OBSERVACOES_CONTACTO,
                a.NOME_ADMINISTRADOR
            FROM CONTACTO c
            JOIN UTENTES_IDOSOS ui ON c.ID_UTENTE = ui.ID_UTENTE
            JOIN UTENTES u ON ui.ID_UTENTE = u.ID_UTENTE
            JOIN ADMINISTRADORES a ON c.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            JOIN TIPO_CONTACTO tc ON c.ID_TIPO_CONTACTO = tc.ID_TIPO_CONTACTO
            JOIN FREQUENCIA_CONTACTO fc ON c.ID_FREQUENCIA_CONTACTO = fc.ID_FREQUENCIA_CONTACTO
            ORDER BY c.DATA_CONTACTO DESC
        """)
        todos_contactos = cursor.fetchall()

    paginator = Paginator(todos_contactos, 20)  # 20 por página (ajustável)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, "contactos/listar_contactos.html", {
        "contactos": page_obj,
    })

@login_required
def detalhe_contacto(request, id):
    with connection.cursor() as cursor:
        # 1. Dados principais do contacto
        cursor.execute("""
            SELECT 
                c.ID_CONTACTO,
                u.NOME_UTENTE AS NOME_IDOSO,
                tc.NOME_TIPO_CONTACTO AS TIPO_CONTACTO,
                c.DATA_CONTACTO,
                fc.DESCRICAO_FREQUENCIA_CONTACTO AS FREQUENCIA,
                c.OBSERVACOES_CONTACTO,
                a.NOME_ADMINISTRADOR,
                u.ID_UTENTE,
                ui.CONTACTO_EMERGENCIA,
                ui.VIVE_SOZINHO,
                g.DESCRICAO_GENERO AS SEXO,
                z.DESCRICAO_ZONA_UTENTE AS ZONA,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS IDADE
            FROM CONTACTO c
            JOIN UTENTES_IDOSOS ui ON c.ID_UTENTE = ui.ID_UTENTE
            JOIN UTENTES u ON ui.ID_UTENTE = u.ID_UTENTE
            JOIN ADMINISTRADORES a ON c.ID_ADMINISTRADOR = a.ID_ADMINISTRADOR
            JOIN TIPO_CONTACTO tc ON c.ID_TIPO_CONTACTO = tc.ID_TIPO_CONTACTO
            JOIN FREQUENCIA_CONTACTO fc ON c.ID_FREQUENCIA_CONTACTO = fc.ID_FREQUENCIA_CONTACTO
            JOIN GENERO g ON u.ID_GENERO = g.ID_GENERO
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            WHERE c.ID_CONTACTO = %s
        """, [id])
        contacto = cursor.fetchone()

        if not contacto:
            messages.error(request, 'Contacto não encontrado.')
            return redirect('contactos_lista')

    return render(request, 'contactos/detalhe_contacto.html', {
        'contacto': contacto,
    })

@login_required
def contactos_novo(request):
    if request.method == 'GET':
        context = {
            'idosos': models.UtentesIdosos.objects.select_related('id_utente').all(),
            'tipos_contacto': models.TipoContacto.objects.all(),
            'frequencias_contacto': models.FrequenciaContacto.objects.all(),
        }
        return render(request, 'contactos/novo_contacto.html', context)

    if request.method == 'POST':
        # Recolher dados
        id_utente = request.POST.get('idoso')
        id_tipo_contacto = request.POST.get('tipo_contacto')
        id_frequencia_contacto = request.POST.get('frequencia_contacto')
        data_contacto = request.POST.get('data_contacto')
        observacoes = request.POST.get('observacoes', '').strip()

        # Validações
        errors = []
        if not id_utente:
            errors.append('É necessário selecionar um idoso.')
        else:
            try:
                idoso = models.UtentesIdosos.objects.get(pk=id_utente)
            except models.UtentesIdosos.DoesNotExist:
                errors.append('Idoso selecionado inválido.')

        if not id_tipo_contacto:
            errors.append('O tipo de contacto é obrigatório.')
        if not data_contacto:
            errors.append('A data do contacto é obrigatória.')

        if errors:
            for err in errors:
                messages.error(request, err)
            
            return redirect('contactos_novo')

        # Obter o ID do administrador a partir do email do utilizador autenticado
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ID_ADMINISTRADOR FROM ADMINISTRADORES WHERE EMAIL_ADMINISTRADOR = %s",
                [request.user.email]
            )
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Utilizador não está registado como administrador.')
                return redirect('contactos_lista')
            id_administrador = row[0]

        try:
            with transaction.atomic():
                contacto = models.Contacto.objects.create(
                    id_administrador_id=id_administrador,
                    id_tipo_contacto_id=id_tipo_contacto,
                    id_frequencia_contacto_id=id_frequencia_contacto if id_frequencia_contacto else None,
                    id_utente_id=id_utente,
                    data_contacto=data_contacto,
                    observacoes_contacto=observacoes,
                )
            messages.success(request, f'Contacto #{contacto.id_contacto} criado com sucesso!')
            return redirect('contactos_detalhe', id=contacto.id_contacto)

        except Exception as e:
            messages.error(request, f'Erro ao criar contacto: {str(e)}')

    return redirect('contactos_lista')

@login_required
def contactos_editar(request, id):
    contacto = get_object_or_404(models.Contacto, pk=id)

    if request.method == 'GET':
        # Preparar submetido com os valores atuais
        submetido = {
            'idoso': str(contacto.id_utente_id),
            'tipo_contacto': str(contacto.id_tipo_contacto_id) if contacto.id_tipo_contacto_id else '',
            'frequencia_contacto': str(contacto.id_frequencia_contacto_id) if contacto.id_frequencia_contacto_id else '',
            'data_contacto': contacto.data_contacto.isoformat() if contacto.data_contacto else '',
            'observacoes': contacto.observacoes_contacto or '',
        }
        context = {
            'contacto': contacto,
            'idosos': models.UtentesIdosos.objects.select_related('id_utente').all(),
            'tipos_contacto': models.TipoContacto.objects.all(),
            'frequencias_contacto': models.FrequenciaContacto.objects.all(),
            'submetido': submetido,
        }
        return render(request, 'contactos/editar_contacto.html', context)

    if request.method == 'POST':
        # Recolher dados (inclui idoso)
        id_utente = request.POST.get('idoso')
        id_tipo_contacto = request.POST.get('tipo_contacto')
        id_frequencia_contacto = request.POST.get('frequencia_contacto')
        data_contacto = request.POST.get('data_contacto')
        observacoes = request.POST.get('observacoes', '').strip()

        # Validações
        errors = []
        if not id_utente:
            errors.append('É necessário selecionar um idoso.')
        if not id_tipo_contacto:
            errors.append('O tipo de contacto é obrigatório.')
        if not data_contacto:
            errors.append('A data do contacto é obrigatória.')

        if errors:
            for err in errors:
                messages.error(request, err)
            # Reexibir o formulário com os dados submetidos (para manter os valores)
            submetido = {
                'idoso': id_utente,
                'tipo_contacto': id_tipo_contacto,
                'frequencia_contacto': id_frequencia_contacto,
                'data_contacto': data_contacto,
                'observacoes': observacoes,
            }
            context = {
                'contacto': contacto,
                'idosos': models.UtentesIdosos.objects.select_related('id_utente').all(),
                'tipos_contacto': models.TipoContacto.objects.all(),
                'frequencias_contacto': models.FrequenciaContacto.objects.all(),
                'submetido': submetido,
            }
            return render(request, 'contactos/editar_contacto.html', context)

        try:
            with transaction.atomic():
                contacto.id_utente_id = id_utente
                contacto.id_tipo_contacto_id = id_tipo_contacto
                contacto.id_frequencia_contacto_id = id_frequencia_contacto if id_frequencia_contacto else None
                contacto.data_contacto = data_contacto
                contacto.observacoes_contacto = observacoes
                contacto.save()
            messages.success(request, f'Contacto #{contacto.id_contacto} atualizado com sucesso!')
            return redirect('contactos_detalhe', id=contacto.id_contacto)

        except Exception as e:
            messages.error(request, f'Erro ao atualizar contacto: {str(e)}')

    return redirect('contactos_lista')

@login_required
def contactos_eliminar(request, id):
    # Verificar se o contacto existe
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ID_CONTACTO FROM CONTACTO WHERE ID_CONTACTO = %s",
            [id]
        )
        if not cursor.fetchone():
            messages.error(request, 'Contacto não encontrado.')
            return redirect('contactos_lista')

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM CONTACTO WHERE ID_CONTACTO = %s",
                    [id]
                )
        messages.success(request, f'Contacto #{id} eliminado com sucesso.')
    except Exception as e:
        messages.error(request, f'Erro ao eliminar contacto: {str(e)}')

    return redirect('contactos_lista')