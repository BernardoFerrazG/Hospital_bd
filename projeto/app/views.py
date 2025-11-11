from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .models import Pessoa, Funcionario, Medico, Paciente, Enfermeiro, Departamento, Administrador, FuncionarioTrabalhaEm


# Create your views here.
# serve para criar a logica do que vai ser exibido nas telas do nosso app
# cada funcao representa uma tela do nosso app

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Pessoa



def cadastro(request):
    if request.method == "GET":
        return render(request, "usuarios/cadastro.html")
    

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


def cadastro_medico(request):
    # Tenta recuperar pessoa por sessão / querystring (se você ainda usar essa mecânica)
    cpf_session = request.session.get('cpf') if hasattr(request, 'session') else None
    cpf_get = request.GET.get('cpf')
    pessoa = None
    if cpf_session:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_session)
        except Pessoa.DoesNotExist:
            pessoa = None
    elif cpf_get:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_get)
        except Pessoa.DoesNotExist:
            pessoa = None

    if request.method == "GET":
        # Se a view foi chamada após o cadastro inicial você pode passar 'pessoa' no contexto
        return render(request, "usuarios/cadastro_medico.html", {"pessoa": pessoa})

    # POST: lê campos mínimos
    crm = request.POST.get("crm", "").strip()
    cpf_hidden = request.POST.get("cpf", "").strip()           # hidden se a view passou pessoa
    cpf_confirm = request.POST.get("cpf_confirm", "").strip() # o que o usuário digitou para confirmar

    if not (crm and cpf_confirm):
        return HttpResponse("Campos obrigatórios: CRM e confirmação do CPF.", status=400)

    # Decide o CPF real a usar:
    # - se veio cpf_hidden (pessoa no contexto), exige que cpf_confirm == cpf_hidden
    # - se não veio, cpf_confirm será usado como o CPF para buscar/criar pessoa
    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    # Tenta obter a Pessoa; se não existir, retornamos erro (ou você pode optar por criar a Pessoa aqui)
    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada com esse CPF. Faça primeiro o cadastro inicial.", status=404)

    # Valida CRM único
    if Medico.objects.filter(crm=crm).exists():
        return HttpResponse("CRM já cadastrado.", status=400)

    # Cria/atualiza Funcionario e Medico com valores default (salario/horas = 0)
    try:
        with transaction.atomic():
            func, criado = Funcionario.objects.get_or_create(
                fcpf=pessoa_obj,
                defaults={
                    "salario": 0,
                    "horas_trabalhadas": 0
                }
            )
            if not criado:
                # mantém salario e horas ou atualiza se quiser; aqui deixamos como estavam
                pass

            Medico.objects.create(
                crm=crm,
                mcpf=func
            )
    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar médico: {e}", status=500)

    return redirect(reverse("login"))



def cadastro_admin(request):
    # tenta recuperar pessoa por sessão ou querystring (compatível com restante do fluxo)
    cpf_session = request.session.get('cpf') if hasattr(request, 'session') else None
    cpf_get = request.GET.get('cpf')
    pessoa = None
    if cpf_session:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_session)
        except Pessoa.DoesNotExist:
            pessoa = None
    elif cpf_get:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_get)
        except Pessoa.DoesNotExist:
            pessoa = None

    if request.method == "GET":
        return render(request, "usuarios/cadastro_admin.html", {"pessoa": pessoa})

    # POST
    cpf_hidden = request.POST.get("cpf", "").strip()
    cpf_confirm = request.POST.get("cpf_confirm", "").strip()

    if not cpf_confirm:
        return HttpResponse("CPF de confirmação é obrigatório.", status=400)

    # Decide o CPF real (se veio hidden, exige correspondência)
    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    # Recupera Pessoa; se não existir, pede cadastro inicial (padrão do projeto)
    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada com esse CPF. Faça primeiro o cadastro inicial.", status=404)

    # Verifica se já existe administrador para esse funcionario
    # Primeiro: garante que exista Funcionario para essa pessoa (get_or_create)
    try:
        with transaction.atomic():
            func, criado = Funcionario.objects.get_or_create(
                fcpf=pessoa_obj,
                defaults={
                    "salario": 0,
                    "horas_trabalhadas": 0
                }
            )

            # Checa se já existe Administrador com esse fcpf (acpf)
            if Administrador.objects.filter(acpf=func).exists():
                return HttpResponse("Já existe um administrador vinculado a esse funcionário/CPF.", status=400)

            Administrador.objects.create(acpf=func)

            # limpa cpf da sessão se existir
            if 'cpf' in request.session:
                try:
                    request.session.pop('cpf', None)
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar administrador: {e}", status=500)

    # redireciona para a home do admin
    return redirect(reverse("login"))

def cadastro_paciente(request):
    # tenta recuperar pessoa por sessão ou querystring (compatível com o restante do fluxo)
    cpf_session = request.session.get('cpf') if hasattr(request, 'session') else None
    cpf_get = request.GET.get('cpf')
    pessoa = None
    if cpf_session:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_session)
        except Pessoa.DoesNotExist:
            pessoa = None
    elif cpf_get:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_get)
        except Pessoa.DoesNotExist:
            pessoa = None

    if request.method == "GET":
        return render(request, "usuarios/cadastro_paciente.html", {"pessoa": pessoa})

    # POST
    cpf_hidden = request.POST.get("cpf", "").strip()
    cpf_confirm = request.POST.get("cpf_confirm", "").strip()

    if not cpf_confirm:
        return HttpResponse("CPF de confirmação é obrigatório.", status=400)

    # Decide o CPF real
    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    # Tenta obter Pessoa; se não existir, pede para cadastrar inicialmente
    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada com esse CPF. Faça primeiro o cadastro inicial.", status=404)

    # Verifica se já existe paciente com esse CPF
    if Paciente.objects.filter(pcpf=pessoa_obj).exists():
        return HttpResponse("Já existe um paciente cadastrado com esse CPF.", status=400)

    try:
        with transaction.atomic():
            # cria o paciente
            Paciente.objects.create(
                pcpf=pessoa_obj
            )

            # limpa cpf da sessão se existir
            if 'cpf' in request.session:
                try:
                    request.session.pop('cpf', None)
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar paciente: {e}", status=500)

    # redireciona para a home geral (ajuste se quiser outra rota)
    return redirect(reverse("login"))


def cadastro_enfermeiro(request):
    # tenta recuperar pessoa por sessão ou querystring (se usar esse fluxo)
    cpf_session = request.session.get('cpf') if hasattr(request, 'session') else None
    cpf_get = request.GET.get('cpf')
    pessoa = None
    if cpf_session:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_session)
        except Pessoa.DoesNotExist:
            pessoa = None
    elif cpf_get:
        try:
            pessoa = Pessoa.objects.get(cpf=cpf_get)
        except Pessoa.DoesNotExist:
            pessoa = None

    if request.method == "GET":
        return render(request, "usuarios/cadastro_enfermeiro.html", {"pessoa": pessoa})

    # POST
    coren = request.POST.get("coren", "").strip()
    cpf_hidden = request.POST.get("cpf", "").strip()
    cpf_confirm = request.POST.get("cpf_confirm", "").strip()

    if not (coren and cpf_confirm):
        return HttpResponse("Campos obrigatórios: COREN e confirmação do CPF.", status=400)

    # Decide o CPF real
    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    # Tenta obter Pessoa; se não existir, informe para cadastrar primeiro (ou remova essa restrição se preferir criar automaticamente)
    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada com esse CPF. Faça primeiro o cadastro inicial.", status=404)

    # Valida COREN único
    if Enfermeiro.objects.filter(coren=coren).exists():
        return HttpResponse("COREN já cadastrado.", status=400)

    try:
        with transaction.atomic():
            func, criado = Funcionario.objects.get_or_create(
                fcpf=pessoa_obj,
                defaults={
                    "salario": 0,
                    "horas_trabalhadas": 0
                }
            )
            if not criado:
                # optional: atualizar salario/horas se quiser
                pass

            # cria o enfermeiro
            Enfermeiro.objects.create(
                coren=coren,
                ecpf=func
            )

            # limpa cpf da sessão se existir
            if 'cpf' in request.session:
                try:
                    request.session.pop('cpf', None)
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar enfermeiro: {e}", status=500)

    # redireciona para home_enf após sucesso
    return redirect(reverse("login"))



def login(request):
    if request.method == "GET":
        return render(request, "usuarios/login.html")

    username = request.POST.get("nome")
    senha = request.POST.get("senha")

    user = authenticate(username=username, password=senha)

    if not user:
        return HttpResponse("Credenciais inválidas!")

    # Login Django
    login_django(request, user)

    # Descobre a pessoa correspondente
    try:
        pessoa = Pessoa.objects.get(nome=username)
    except Pessoa.DoesNotExist:
        return HttpResponse("Usuário não encontrado no banco de pessoas.", status=404)

    # Tenta achar se ele é funcionário
    funcionario = Funcionario.objects.filter(fcpf=pessoa.cpf).first()

    # Verifica o tipo de papel (função)
    if funcionario:
        if Medico.objects.filter(mcpf=funcionario.fcpf).exists():
            return redirect(reverse("home_med"))
        elif Enfermeiro.objects.filter(ecpf=funcionario.fcpf).exists():
            return redirect(reverse("home_enf"))
        elif Administrador.objects.filter(acpf=funcionario.fcpf).exists():
            return redirect(reverse("home_admin"))
    else:
        if Paciente.objects.filter(pcpf=pessoa.cpf).exists():
            return redirect(reverse("home"))
    
    return HttpResponse("Papel do usuário não identificado.", status=403)
        



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