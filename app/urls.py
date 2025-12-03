from django.urls import path
from app import views
from app.paciente import views as paciente_views
from app.medico.views import listar_salas, alocar_sala, listar_leitos, alocar_leito
from . import views

urlpatterns = [

    path('', views.landing, name='landing'),

    path('cadastro/', views.cadastro_paciente, name='cadastro'),

    path('cadastro/medico/', views.cadastro_medico, name='cadastro_medico'),
    path('cadastro/enfermeiro/', views.cadastro_enfermeiro, name='cadastro_enfermeiro'),

    path('login/', views.login_paciente, name='login'),
    path('home/', views.home, name='home'),
    path('home_med/', views.home_med, name='home_med'),
    path('home_enf/', views.home_enf, name='home_enf'),

    path('alocar/enfermeiro/', views.enfermeiro_alocacoes, name='enfermeiro_alocacoes'),


    path('medico/salas/', listar_salas, name='listar_salas'),
    path('medico/salas/alocar/', alocar_sala, name='alocar_sala'),

    path('medico/leitos/', listar_leitos, name='listar_leitos'),
    path('medico/leitos/alocar/', alocar_leito, name='alocar_leito'),


    path('paciente/agenda/', paciente_views.minha_agenda, name='minha_agenda'),

    path('paciente/historico/', paciente_views.consultar_historico, name='consultar_historico'),

    path('paciente/agendar/consulta/', paciente_views.marcar_consulta, name='marcar_consulta'),
    path('paciente/agendar/cirurgia/', paciente_views.marcar_cirurgia, name='marcar_cirurgia'),


    path("cadastro_admin/", views.cadastro_adm, name="cadastro_adm"),
    path('login_adm/', views.login_adm, name='login_adm'),
    path("home_adm/", views.home_adm, name="home_adm"),
    path("leitos_admin/", views.leitos_adm, name="leitos_adm"),
    path("salas_cirurgia_admin/", views.salas_cirurgia_adm, name="salas_cirurgia_adm"),
    path("consultorios_admin/", views.consultorios_adm, name="consultorios_adm"),
    path("enfermeiros_admin/", views.enfermeiros_adm, name="enfermeiros_adm"),
    path("medicos_adm/", views.medicos_adm, name="medicos_adm"),
    path("desalocar_medico/<str:crm>/", views.desalocar_medico, name="desalocar_medico"),
    path("desalocar_enfermeiro/<str:coren>/", views.desalocar_enfermeiro, name="desalocar_enfermeiro"),
    path("salas/remover/<int:numero>/", views.remover_sala, name="remover_sala"),
    path("consultorios/remover/<int:numero>/", views.remover_consultorio, name="remover_consultorio"),
    path("leitos/cirurgia/remover/<int:leito_numero>/", views.remover_leito_cirurgia, name="remover_leito_cirurgia"),
    path("leitos/uti/remover/<int:leito_numero>/", views.remover_leito_uti, name="remover_leito_uti"),
]
