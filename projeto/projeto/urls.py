# Define os links do site
from django.contrib import admin
from django.urls import path, include
from app import views # importa as views do app


urlpatterns = [
    #rota, view responsavel, nome de referencia
    path("", views.cadastro, name="cadastro"),
    path("admin/", admin.site.urls),
    path('auth/', include('app.urls')),
]
