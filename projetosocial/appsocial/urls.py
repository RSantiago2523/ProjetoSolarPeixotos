from django.urls import path
from .views.historico import historico_utente_limpar_tudo, historico_utente_lista, historico_utente_detalhe, historico_idoso_lista, historico_idoso_detalhe, historico_idoso_limpar_tudo
from .views.auth import login_view, logout_view, home
from .views.dashboard import dashboard
from .views.socioeconomicos import socioeconomicos_lista, socioeconomicos_novo, socioeconomicos_detalhe, socioeconomicos_editar, socioeconomicos_eliminar
from .views.idosos import idosos_lista, idosos_detalhe, idosos_novo, idosos_editar, idosos_eliminar
from .views.intervencoes import intervencoes_lista, criar_intervencao, detalhe_intervencao, editar_intervencao, eliminar_intervencao
from .views.encaminhamentos import encaminhamentos_lista, encaminhamentos_detalhe, encaminhamentos_novo, encaminhamentos_editar, encaminhamentos_eliminar, intervencoes_autocomplete
from .views.contactos import listar_contactos, detalhe_contacto, contactos_novo, contactos_editar, contactos_eliminar
from .views.pdf import socioeconomicos_pdf, idosos_pdf
from .views.relatorio_pdf import relatorio_pdf_form, relatorio_pdf

urlpatterns = [

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home, name='home'),

    path('dashboard/', dashboard, name='dashboard'),

    # URLs para Utentes Socioeconómicos
    path('socioeconomicos/', socioeconomicos_lista, name='socioeconomicos_lista'),
    path('socioeconomicos/novo/', socioeconomicos_novo, name='socioeconomicos_novo'),
    path('socioeconomicos/<int:id_utente>/', socioeconomicos_detalhe, name='socioeconomicos_detalhe'),
    path('socioeconomicos/<int:id_utente>/editar/', socioeconomicos_editar, name='socioeconomicos_editar'),
    path('socioeconomicos/<int:id_utente>/eliminar/', socioeconomicos_eliminar, name='socioeconomicos_eliminar'),

    #URLs para Utentes Idosos
    path('idosos/', idosos_lista, name='idosos_lista'),
    path('idosos/<int:id_utente>/', idosos_detalhe, name='idosos_detalhe'),
    path('idosos/novo/', idosos_novo, name='idosos_novo'),
    path('idosos/<int:id_utente>/editar/', idosos_editar, name='idosos_editar'),
    path('idosos/<int:id_utente>/eliminar/', idosos_eliminar, name='idosos_eliminar'),

    #URLs para Intervencoes
    path('intervencoes/', intervencoes_lista, name='intervencoes_lista'),
    path('intervencoes/nova/', criar_intervencao, name='criar_intervencao'),
    path("intervencoes/<int:id>/", detalhe_intervencao, name="detalhe_intervencao"),
    path("intervencoes/<int:id>/editar/", editar_intervencao, name="editar_intervencao"),
    path("intervencoes/<int:id>/eliminar/", eliminar_intervencao, name="eliminar_intervencao"),

    #URLs para Encaminhamentos
    path('encaminhamentos/', encaminhamentos_lista, name='encaminhamentos_lista'),
    path('encaminhamentos/<int:id>/', encaminhamentos_detalhe, name='encaminhamentos_detalhe'),
    path('encaminhamentos/novo/', encaminhamentos_novo, name='encaminhamentos_novo'),
    path('encaminhamentos/<int:id>/editar/', encaminhamentos_editar, name='encaminhamentos_editar'),
    path('encaminhamentos/<int:id>/eliminar/', encaminhamentos_eliminar, name='encaminhamentos_eliminar'),
    path('intervencoes/autocomplete/', intervencoes_autocomplete, name='intervencoes_autocomplete'),

    #URLs para Contactos
    path("contactos/", listar_contactos, name="contactos_lista"),
    path("contactos/<int:id>/", detalhe_contacto, name="contactos_detalhe"),
    path("contactos/novo/", contactos_novo, name="contactos_novo"),
    path("contactos/<int:id>/editar/", contactos_editar, name="contactos_editar"),
    path("contactos/<int:id>/eliminar/", contactos_eliminar, name="contactos_eliminar"),

    #URLs para ficheiros (Socioeconomico)
    path('socioeconomicos/<int:id_utente>/pdf/', socioeconomicos_pdf, name='socioeconomicos_pdf'),
    path('idosos/<int:id_utente>/pdf/', idosos_pdf, name='idosos_pdf'),

    #URLs para Relatórios
    path('relatorio/<int:ano>/', relatorio_pdf, name='relatorio_anual'),
    path('relatorio/<int:ano>/<int:mes>/', relatorio_pdf, name='relatorio_mensal'),
    path('relatorio/', relatorio_pdf_form, name='relatorio_pdf_form'),

    #URLs para Históricos
    path('socioeconomicos/<int:id_utente>/historico/', historico_utente_lista, name='historico_utente_lista'),
    path('socioeconomicos/<int:id_utente>/historico/<int:id_historico>/', historico_utente_detalhe, name='historico_utente_detalhe'),
    path('socioeconomicos/<int:id_utente>/historico/limpar/', historico_utente_limpar_tudo, name='historico_utente_limpar_tudo'),
    path('idosos/<int:id_utente>/historico/', historico_idoso_lista, name='historico_idoso_lista'),
    path('idosos/<int:id_utente>/historico/<int:id_historico>/', historico_idoso_detalhe, name='historico_idoso_detalhe'),
    path('idosos/<int:id_utente>/historico/limpar/', historico_idoso_limpar_tudo, name='historico_idoso_limpar_tudo'),
]