from django.urls import path
from app import views
from app.medico.views import listar_salas, alocar_sala

urlpatterns = [

    path('', views.landing, name='landing'),

    path('cadastro/', views.cadastro, name='cadastro'),

    path('cadastro/medico/', views.cadastro_medico, name='cadastro_medico'),
    path('cadastro/enfermeiro/', views.cadastro_enfermeiro, name='cadastro_enfermeiro'),
    path('cadastro/admin/', views.cadastro_admin, name='cadastro_admin'),
    path('cadastro/paciente/', views.cadastro_paciente, name='cadastro_paciente'),

    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('home_med/', views.home_med, name='home_med'),
    path('home_enf/', views.home_enf, name='home_enf'),
    path('home_admin/', views.home_admin, name='home_admin'),

    path('alocar/', views.alocar_funcionario, name='alocar'),
    path('alocar/enfermeiro/', views.enfermeiro_alocacoes, name='enfermeiro_alocacoes'),


    path('medico/salas/', listar_salas, name='listar_salas'),
    path('medico/salas/alocar/', alocar_sala, name='alocar_sala'),
]
