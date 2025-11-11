from django.urls import path
from app import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),

    path('cadastro/medico/', views.cadastro_medico, name='cadastro_medico'),


    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('home_med/', views.home_med, name='home_med'),
    path('home_enf/', views.home_enf, name='home_enf'),
    path('home_admin/', views.home_admin, name='home_admin'),
    path('alocar/', views.alocar, name='alocar'),
]
