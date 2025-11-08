from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from .models import Usuario

# Create your views here.
# serve para criar a logica do que vai ser exibido nas telas do nosso app
# cada funcao representa uma tela do nosso app

def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")
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
        Usuario.objects.create(user=user, papel=papel)
        
        return HttpResponse("usuario cadastrado com sucesso!")
        
def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        username = request.POST.get("nome")
        senha = request.POST.get("senha")
        papel = request.POST.get("papel")
        
        user = authenticate(username=username, password=senha)
        
        if user:
            usuario = Usuario.objects.filter(user=user).first()
            
            if usuario and usuario.papel == papel:
                login_django(request, user)

                # redireciona conforme o papel
                if papel == "medico":
                    return redirect('/auth/home_med/')
                elif papel == "paciente":
                    return redirect('/auth/home/')
                elif papel == "enfermeiro":
                    return redirect('/auth/home_enf/')
                elif papel == "admin":
                    return redirect('/auth/home_admin/')
                else:
                    return redirect('/auth/home/')
            
            return HttpResponse("Papel incorreto para este usuário!")
        
        # se o authenticate falhar
        return HttpResponse("Credenciais inválidas!")

@login_required(login_url='/auth/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/auth/login/')
def home_med(request):
    return render(request, 'home_med.html')

@login_required(login_url='/auth/login/')
def home_enf(request):
    return render(request, 'home_enf.html')

@login_required(login_url='/auth/login/')
def home_admin(request):
    return render(request, 'home_admin.html')

