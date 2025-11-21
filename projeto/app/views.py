from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Pessoa, Funcionario, Medico, Paciente, Enfermeiro, Departamento, Administrador, FuncionarioTrabalhaEm
from .medico.views import cadastro_medico, home_med
from .enfermeiro.views import cadastro_enfermeiro, home_enf
from .administrador.views import cadastro_admin, home_admin, alocar_funcionario
from .paciente.views import cadastro_paciente, home


def landing(request):
    return render(request, "login/landing.html")


def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastros/cadastro.html")
    

    # POST
    nome = request.POST.get("nome", "").strip()
    cpf = request.POST.get("cpf", "").strip()
    sexo = request.POST.get("sexo", "").strip()
    telefone = request.POST.get("telefone", "").strip()
    email = request.POST.get("email", "").strip()
    data_nascimento = request.POST.get("data_nascimento")
    senha = request.POST.get("senha", "").strip()
    papel = request.POST.get("papel", "").strip().lower()

    if not (nome and cpf and senha and papel):
        return HttpResponse("Campos obrigatórios: nome, cpf, senha e papel.", status=400)

    if Pessoa.objects.filter(cpf=cpf).exists():
        return HttpResponse("CPF já cadastrado.", status=400)

    if User.objects.filter(username=nome).exists():
        return HttpResponse("Usuário já existe.", status=400)

    # Cria Pessoa
    pessoa = Pessoa.objects.create(
        cpf=cpf,
        nome=nome,
        sexo=sexo,
        telefone=telefone,
        email=email,
        data_nascimento=data_nascimento if data_nascimento else None
    )

    # Cria usuário Django (recomendo username=cpf, mas mantenho o seu comportamento)
    user = User.objects.create_user(username=nome, email=email, password=senha)

    # Armazena CPF na sessão e força salvar imediatamente
    request.session['cpf'] = cpf
    try:
        request.session.save()   # força persistir no DB da sessão
    except Exception as e:
        # não falha aqui: apenas loga para diagnóstico
        print("WARN: falha ao salvar sessão:", e)


    # Redireciona para o cadastro específico.
    # Usamos redirect normal e também colocamos CPF na querystring como fallback.
    if papel == "medico":
        return redirect(f"{reverse('cadastro_medico')}?cpf={cpf}")
    elif papel == "enfermeiro":
        return redirect(f"{reverse('cadastro_enfermeiro')}?cpf={cpf}")
    elif papel == "admin":
        return redirect(f"{reverse('cadastro_admin')}?cpf={cpf}")
    elif papel == "paciente":
        return redirect(f"{reverse('cadastro_paciente')}?cpf={cpf}")
    else:
        return HttpResponse("Papel inválido.", status=400)


def login(request):
    if request.method == "GET":
        return render(request, "login/login.html")

    username = request.POST.get("nome", "").strip()   # campo do form
    senha = request.POST.get("senha", "")

    user = authenticate(username=username, password=senha)
    if not user:
        return HttpResponse("Credenciais inválidas!", status=401)

    # efetua o login no django
    login_django(request, user)

    # Tentar encontrar Pessoa: primeiro por CPF (username pode ser cpf), senão por nome
    pessoa = None
    # tentativa 1: CPF exato (11 dígitos ou o que estiver no username)
    pessoa = Pessoa.objects.filter(cpf=username).first()
    if not pessoa:
        # tentativa 2: procurar pelo nome (caso você tenha usado nome como username)
        pessoa = Pessoa.objects.filter(nome=username).first()

    if not pessoa:
        # usuário autenticou mas não tem Pessoa vinculada
        return HttpResponse("Usuário autenticado, mas sem registro na tabela Pessoa.", status=404)

    # tenta achar Funcionario associado (fcpf é OneToOneField para Pessoa)
    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()

    if funcionario:
        # agora verifica qual cargo
        if Medico.objects.filter(mcpf=funcionario).exists():
            return redirect(reverse("home_med"))
        if Enfermeiro.objects.filter(ecpf=funcionario).exists():
            return redirect(reverse("home_enf"))
        if Administrador.objects.filter(acpf=funcionario).exists():
            return redirect(reverse("home_admin"))
        # se for funcionario mas nenhum dos papéis acima:
        return HttpResponse("Funcionário encontrado, mas sem papel (medico/enfermeiro/admin) definido.", status=403)
    else:
        # não é funcionário — verificar se é paciente
        if Paciente.objects.filter(pcpf=pessoa).exists():
            return redirect(reverse("home"))
        else:
            return HttpResponse("Usuário não encontrado como funcionário nem paciente.", status=404)


@login_required(login_url='/auth/login/')
def plataforma(request):
    return HttpResponse("plataforma.")


def enfermeiro_alocacoes(request):
    return render(request, "alocar/enfermeiro_alocacoes.html")

