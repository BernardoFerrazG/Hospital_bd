from django.urls import path
from app import views
from app.medico.views import listar_salas, alocar_sala, listar_leitos, alocar_leito, listar_consultas, gerenciar_salas, desalocar_sala, liberar_leito

urlpatterns = [

    path('', views.landing, name='landing'),

    path('cadastro/', views.cadastro, name='cadastro'),

    path('cadastro/medico/', views.cadastro_medico, name='cadastro_medico'),
    path('cadastro/enfermeiro/', views.cadastro_enfermeiro, name='cadastro_enfermeiro'),
    path('cadastro/admin/', views.cadastro_admin, name='cadastro_admin'),
    path('cadastro/paciente/', views.cadastro_paciente, name='cadastro_paciente'),

    path('login/', views.login, name='login'),
    path('login/enfermeiro/', views.login_enfermeiro, name='login_enfermeiro'),
    path('home/', views.home, name='home'),
    path('home_med/', views.home_med, name='home_med'),
    path('home_enf/', views.home_enf, name='home_enf'),
    path('home_admin/', views.home_admin, name='home_admin'),

    path('alocar/', views.alocar_funcionario, name='alocar'),
    path('alocar/enfermeiro/', views.enfermeiro_alocacoes, name='enfermeiro_alocacoes'),


    path('medico/salas/', listar_salas, name='listar_salas'),
    path('medico/salas/alocar/', alocar_sala, name='alocar_sala'),

    path('medico/leitos/', listar_leitos, name='listar_leitos'),
    path('medico/leitos/alocar/', alocar_leito, name='alocar_leito'),

    path('medico/consultas/', listar_consultas, name='listar_consultas'),

    path('medico/salas/meus/', gerenciar_salas, name='gerenciar_salas'),
    path('medico/salas/desalocar/', desalocar_sala, name='desalocar_sala'),
    path('medico/salas/liberar_leito/', liberar_leito, name='liberar_leito'),
    ]
