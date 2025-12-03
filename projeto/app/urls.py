from django.urls import path
from . import views

urlpatterns = [
    path("cadastro_admin/", views.cadastro_adm, name="cadastro_adm"),
    path('login/', views.login_adm, name='login_adm'),
    path("home_adm/", views.home_adm, name="home_adm"),
    path("leitos_admin/", views.leitos_adm, name="leitos_adm"),
    path("salas_cirurgia_admin/", views.salas_cirurgia_adm, name="salas_cirurgia_adm"),
    path("consultorios_admin/", views.consultorios_adm, name="consultorios_adm"),
    path("enfermeiros_admin/", views.enfermeiros_adm, name="enfermeiros_adm"),
    path("medicos_adm/", views.medicos_adm, name="medicos_adm"),
    path("desalocar_medico/<str:crm>/", views.desalocar_medico, name="desalocar_medico"),
    path("desalocar_enfermeiro/<str:coren>/", views.desalocar_enfermeiro, name="desalocar_enfermeiro"),
]
