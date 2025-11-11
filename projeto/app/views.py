from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .models import Pessoa, Funcionario, Medico, Departamento, FuncionarioTrabalhaEm


# Create your views here.
# serve para criar a logica do que vai ser exibido nas telas do nosso app
# cada funcao representa uma tela do nosso app

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Pessoa



def cadastro(request):
    if request.method == "GET":
        print("DEBUG: método GET recebido no cadastro")
        return render(request, "usuarios/cadastro.html")
    

    print("DEBUG: dados recebidos no cadastro:", request.POST)
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

    # DEBUG: imprime no terminal para você checar
    print("DEBUG: cpf salvo na sessao (server) =", request.session.get('cpf'))

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


def cadastro_medico(request):
    # tentamos primeiro obter cpf da sessão; se não tiver, pegamos da querystring (?cpf=)
    cpf = request.session.get('cpf') or request.GET.get('cpf')
    if not cpf:
        return HttpResponse("Sessão expirada. Volte para o cadastro inicial.", status=400)

    try:
        pessoa = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada.", status=404)

    if request.method == "GET":
        return render(request, "usuarios/cadastro_medico.html")

    crm = request.POST.get("crm", "").strip()
    salario = request.POST.get("salario") or 0
    horas_trabalhadas = request.POST.get("horas_trabalhadas") or 0

    if Medico.objects.filter(crm=crm).exists():
        return HttpResponse("CRM já cadastrado.", status=400)

    try:
        with transaction.atomic():
            func, criado = Funcionario.objects.get_or_create(
                fcpf=pessoa,
                defaults={
                    "salario": salario,
                    "horas_trabalhadas": horas_trabalhadas
                }
            )
            if not criado:
                func.salario = salario
                func.horas_trabalhadas = horas_trabalhadas
                func.save()

            Medico.objects.create(
                crm=crm,
                mcpf=func
            )

            # Remove o cpf da sessão depois que terminar, se existir
            if 'cpf' in request.session:
                try:
                    del request.session['cpf']
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar médico: {e}", status=500)

    return HttpResponse("Médico cadastrado com sucesso!")



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


@login_required(login_url='/auth/login/')
def home(request):
    return render(request, "usuarios/home.html")

@login_required(login_url='/auth/login/')
def home_med(request):
    return render(request, "usuarios/home_med.html")

@login_required(login_url='/auth/login/')
def home_enf(request):
    return render(request, "usuarios/home_enf.html")

@login_required(login_url='/auth/login/')
def home_admin(request):
    return render(request, "usuarios/home_admin.html")

@login_required(login_url='/auth/login/')
def alocar(request):
    if request.method == "GET":
        funcionarios = Funcionario.objects.all()
        departamentos = Departamento.objects.all()
        return render(request, "usuarios/alocar.html", {
            "funcionarios": funcionarios,
            "departamentos": departamentos
        })

    elif request.method == "POST":
        cpf_funcionario = request.POST.get("cpf_funcionario")
        nome_departamento = request.POST.get("nome_departamento")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")

        funcionario = Funcionario.objects.get(fcpf=cpf_funcionario)
        departamento = Departamento.objects.get(dnome=nome_departamento)

        FuncionarioTrabalhaEm.objects.create(
            cpf_funcionario=funcionario,
            nome_departamento=departamento,
            data_inicio=data_inicio or None,
            data_fim=data_fim or None
        )

        return HttpResponse("Funcionário alocado com sucesso!")