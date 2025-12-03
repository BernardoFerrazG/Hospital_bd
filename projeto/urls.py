from django.urls import path, include
from app import views
from app.medico.views import listar_salas, alocar_sala, listar_leitos, alocar_leito
from app.paciente import views as paciente_views
from django.contrib import admin
from django.shortcuts import redirect


urlpatterns = [

    path("admin/", admin.site.urls),
    path("auth/", include("app.urls")),  # tudo do app fica dentro de /auth/
    path("", lambda request: redirect("login_adm")),


]
