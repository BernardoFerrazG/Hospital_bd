from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("app.urls")),  # tudo do app fica dentro de /auth/
    path("", lambda request: redirect("login_adm")),
]
