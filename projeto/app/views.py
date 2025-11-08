from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required

# Create your views here.
# serve para criar a logica do que vai ser exibido nas telas do nosso app
# cada funcao representa uma tela do nosso app

def cadastro(request):
    if request.method == "GET":
        return render(request, "usuarios/cadastro.html")
    else:
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        papel = request.POST.get("papel")
        
        user = User.objects.filter(username=nome).first()
        
        if user:
            return HttpResponse("Usuário já existe!")
        
        user = User.objects.create_user(username=nome, email=email, password=senha)
        user.save()
        
        return HttpResponse("usuario cadastrado com sucesso!")
        
def login(request):
    if request.method == "GET":
        return render(request, "usuarios/login.html")
    else:
        username = request.POST.get("nome")
        senha = request.POST.get("senha")
        
        user = authenticate(username=username, password=senha)
        
        if user:
            login_django (request, user)
            return HttpResponse("Login realizado com sucesso!")
        else:
            return HttpResponse("Credenciais inválidas!")

@login_required(login_url='/auth/login/')
def plataforma(request):
    return HttpResponse("plataforma.")
