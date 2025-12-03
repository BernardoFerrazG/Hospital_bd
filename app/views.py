from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Pessoa, Funcionario, Medico, Paciente, Enfermeiro, Departamento, Administrador, Consultorio
from .medico.views import cadastro_medico, home_med
from .enfermeiro.views import cadastro_enfermeiro, home_enf, enfermeiro_alocacoes
from .paciente.views import cadastro_paciente, home
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import LeitoCirurgico, LeitoUTI


def landing(request):
    return render(request, "login/landing.html")


def cadastro_paciente(request):
    if request.method == "GET":
        return render(request, "cadastros/cadastro_paciente.html") 
    
    nome = request.POST.get("nome", "").strip()
    cpf = request.POST.get("cpf", "").strip()
    sexo = request.POST.get("sexo", "").strip()
    telefone = request.POST.get("telefone", "").strip()
    email = request.POST.get("email", "").strip()
    data_nascimento = request.POST.get("data_nascimento")
    senha = request.POST.get("senha", "").strip()

    if not (nome and cpf and senha):
        messages.error(request, "Campos obrigatórios: nome, cpf e senha.")
        return redirect('cadastro')

    if Pessoa.objects.filter(cpf=cpf).exists():
        messages.error(request, "CPF já cadastrado.")
        return redirect('cadastro')

    # 1️⃣ Cria Pessoa
    pessoa = Pessoa.objects.create(
        cpf=cpf,
        nome=nome,
        sexo=sexo,
        telefone=telefone,
        email=email,
        data_nascimento=data_nascimento if data_nascimento else None,
        senha=make_password(senha) # Salva a senha hasheada
    )

    # 2️⃣ Cria Usuário Django (para o login padrão)
    User.objects.create_user(username=cpf, email=email, password=senha) 
    
    # 3️⃣ Cria o registro de Paciente (Sem funcionalidade extra)
    Paciente.objects.create(pcpf=pessoa)
    
    messages.success(request, "Cadastro de paciente realizado com sucesso! Faça login.")
    return redirect('login') # Redireciona para o login base


def login_paciente(request):
    if request.method == "GET":
        return render(request, "login/login_paciente.html") 

    username = request.POST.get("cpf", "").strip() # Vamos usar CPF como username/identificador
    senha = request.POST.get("senha", "")
    
    # Busca a Pessoa pelo CPF (username)
    try:
        pessoa = Pessoa.objects.get(cpf=username)
    except Pessoa.DoesNotExist:
        messages.error(request, "CPF não encontrado!")
        return redirect("login")

    # Verifica a senha com o hash da tabela Pessoa
    if not check_password(senha, pessoa.senha):
        messages.error(request, "Senha incorreta!")
        return redirect("login")

    # Verifica se é um Paciente (Usando o modelo Paciente)
    if Paciente.objects.filter(pcpf=pessoa).exists():
        
        user = User.objects.get(username=username) 
        login_django(request, user) 
    
        request.session['usuario_id'] = pessoa.cpf
        request.session['tipo'] = 'paciente'
        
        messages.success(request, f"Bem-vindo(a), {pessoa.nome}!")
        return redirect('home') # Redireciona para a home do paciente
    else:
        messages.error(request, "Acesso negado. Você não está registrado como paciente.")
        return redirect("login")

def cadastro_adm(request):

    if request.method == "POST":

        cpf = request.POST.get("cpf")
        nome = request.POST.get("nome")
        sexo = request.POST.get("sexo")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        data_nascimento = request.POST.get("data_nascimento")
        senha = request.POST.get("senha")
        departamento_nome = request.POST.get("departamento")
        salario = request.POST.get("salario")
        horas = request.POST.get("horas_trabalhadas")

        # 1️⃣  Verificar duplicações
        if Pessoa.objects.filter(cpf=cpf).exists():
            messages.error(request, "Já existe alguém com esse CPF!")
            return redirect("cadastro_adm")

        # 2️⃣ Criar Pessoa
        pessoa = Pessoa.objects.create(
            cpf=cpf,
            nome=nome,
            sexo=sexo,
            telefone=telefone,
            email=email,
            data_nascimento=data_nascimento,
            senha=make_password(senha)
        )

        # 3️⃣ Criar Funcionário
        funcionario = Funcionario.objects.create(
            fcpf=pessoa,
            salario=salario,
            horas_trabalhadas=horas
        )

        # 4️⃣ Criar Administrador
        administrador = Administrador.objects.create(
            acpf=funcionario
        )

        # 5️⃣ Criar Departamento
        Departamento.objects.create(
            dnome=departamento_nome,
            cpf_administrador=administrador
        )

        messages.success(request, "Administrador cadastrado com sucesso!")
        return redirect("login_adm")

    return render(request, "usuarios/cadastro_adm.html")

def login_adm(request):
    if request.method == "POST":
        cpf = request.POST.get("cpf")
        senha = request.POST.get("senha")

        try:
            pessoa = Pessoa.objects.get(cpf=cpf)
        except Pessoa.DoesNotExist:
            messages.error(request, "CPF não encontrado!")
            return redirect("login_adm")

        if not check_password(senha, pessoa.senha):
            messages.error(request, "Senha incorreta!")
            return redirect("login_adm")

        try:
            funcionario = Funcionario.objects.get(fcpf=pessoa)
        except Funcionario.DoesNotExist:
            messages.error(request, "Você não é funcionário!")
            return redirect("login_adm")

        try:
            Administrador.objects.get(acpf=funcionario)
        except Administrador.DoesNotExist:
            messages.error(request, "Você não é administrador!")
            return redirect("login_adm")

        # ✅ CRIA SESSÃO DO ADMIN
        request.session['usuario_id'] = pessoa.cpf
        request.session['tipo'] = 'admin'

        messages.success(request, f"Bem-vindo(a), {pessoa.nome}!")
        return redirect("home_adm")

    return render(request, "usuarios/login_adm.html")



def home_adm(request):
    # Verifica se o administrador está logado
    if request.session.get('tipo') != 'admin':
        messages.error(request, "Você precisa estar logado!")
        return redirect("login_adm")

    return render(request, "usuarios/home_adm.html")


    


def leitos_adm(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        if tipo == "Cirurgia":
            LeitoCirurgico.objects.create(
                departamento=request.POST.get("departamento"),
                fenfermeiro=None,
                fpaciente=None,
                status="Disponível"
            )
        elif tipo == "UTI":
            LeitoUTI.objects.create(
                departamento=request.POST.get("departamento"),
                fenfermeiro=None,
                fpaciente=None,
                status="Disponível"
            )
        return redirect("leitos_adm")

    leitos_cirurgia = LeitoCirurgico.objects.all()
    leitos_uti = LeitoUTI.objects.all()
    return render(
        request, 
        "usuarios/leitos_adm.html", 
        {"leitos_cirurgia": leitos_cirurgia, "leitos_uti": leitos_uti}
    )

def remover_leito_cirurgia(request, leito_numero):
    leito = get_object_or_404(LeitoCirurgico, numero=leito_numero)
    leito.delete()
    return redirect("leitos_adm")

def remover_leito_uti(request, leito_numero):
    leito = get_object_or_404(LeitoUTI, numero=leito_numero)
    leito.delete()
    return redirect("leitos_adm")

def consultorios_adm(request):

    # ───────────────────────────────
    # CADASTRAR CONSULTÓRIO
    # ───────────────────────────────
    if request.method == "POST":
        numero = request.POST.get("numero")
        status = request.POST.get("status")
        andar = request.POST.get("andar")

        # número vem como “C-01”? então salvamos apenas a parte numérica
        # ou você pode usar exatamente como vem — aqui vou manter literal.
        try:
            numero_int = int(numero.replace("C-", ""))   # converte "C-01" → 1
        except:
            numero_int = numero   # caso queira manter número literal

        Consultorio.objects.create(
            andar=andar,                   # 🔥 você não tem campo "andar" no HTML, defino fixo
            numero=numero_int,
            status=status,
            departamento=None,
            fmedico=None
        )

        return redirect("consultorios_adm")

    # ───────────────────────────────
    # LISTAR CONSULTÓRIOS
    # ───────────────────────────────
    consultorios = Consultorio.objects.all()

    return render(
        request,
        "usuarios/consultorios_adm.html",
        {"consultorios": consultorios}
    )
def remover_consultorio(request, numero):
    Consultorio.objects.filter(numero=numero).delete()
    return redirect("consultorios_adm")
from .models import SalaCirurgia

def salas_cirurgia_adm(request):

    # ───────────────────────────────
    # CADASTRAR SALA DE CIRURGIA
    # ───────────────────────────────
    if request.method == "POST":
        numero = request.POST.get("numero")
        status = request.POST.get("status")

        # Converte "SC-01" → 1
        try:
            numero_int = int(numero.replace("SC-", ""))
        except:
            numero_int = None

        SalaCirurgia.objects.create(
            numero=numero_int,
            status=status,
            departamento=None,
            fmedico=None,
            fenfermeiro=None
        )

        return redirect("salas_cirurgia_adm")

    # ───────────────────────────────
    # LISTAR SALAS DE CIRURGIA
    # ───────────────────────────────
    salas = SalaCirurgia.objects.all().order_by("numero")

    return render(
        request,
        "usuarios/salas_cirurgia_adm.html",
        {"salas": salas}
    )

def remover_sala(request, numero):
    SalaCirurgia.objects.filter(numero=numero).delete()
    return redirect("salas_cirurgia_adm")


from django.shortcuts import render, redirect
from .models import Medico, Consultorio, MedicoTrabalhaConsultorio, EnfermeiroTrabalhaConsultorio, Enfermeiro

def medicos_adm(request):

    if request.method == "POST":
        crm = request.POST.get("medico")
        consultorio = request.POST.get("consultorio")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")

        # Buscar o OBJETO Medico (não uma string)
        medico_obj = Medico.objects.get(crm=crm)

        # Parse andar-numero
        andar, numero = consultorio.split("-")

        MedicoTrabalhaConsultorio.objects.create(
            crm_medico=medico_obj,   # <- AGORA É UM OBJETO
            andar=andar,
            numero=numero,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        return redirect("medicos_adm")

    context = {
        "medicos": Medico.objects.select_related("mcpf").all(),
        "consultorios": Consultorio.objects.all(),
        "alocacoes": MedicoTrabalhaConsultorio.objects.all(),
    }

    return render(request, "usuarios/medicos_adm.html", context)

def desalocar_medico(request, crm):
    MedicoTrabalhaConsultorio.objects.filter(crm_medico__crm=crm).delete()
    return redirect("medicos_adm")



def enfermeiros_adm(request):

    if request.method == "POST":
        coren_enfermeiro = request.POST.get("enfermeiro")  # aqui espere o coren (string)
        consultorio = request.POST.get("consultorio")
        data_inicio = request.POST.get("data_inicio")
        data_fim = request.POST.get("data_fim")

        # Buscar a INSTÂNCIA do Enfermeiro (não a string)
        enfermeiro_obj = Enfermeiro.objects.get(coren=coren_enfermeiro)

        # Parse andar-numero (converte pra int para ficar consistente)
        andar_str, numero_str = consultorio.split("-")
        try:
            andar = int(andar_str)
            numero = int(numero_str)
        except ValueError:
            # se o formato for diferente, mantenha como string
            andar = andar_str
            numero = numero_str

        EnfermeiroTrabalhaConsultorio.objects.create(
            coren_enfermeiro=enfermeiro_obj,   # INSTÂNCIA aqui
            andar=andar,
            numero=numero,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        return redirect("enfermeiros_adm")

    context = {
        "enfermeiros": Enfermeiro.objects.select_related("ecpf").all(),
        "consultorios": Consultorio.objects.all(),
        "alocacoes": EnfermeiroTrabalhaConsultorio.objects.all(),
    }

    return render(request, "usuarios/enfermeiros_adm.html", context)

def desalocar_enfermeiro(request, coren):
    EnfermeiroTrabalhaConsultorio.objects.filter(coren_enfermeiro__coren=coren).delete()
    return redirect("enfermeiros_adm")

@login_required(login_url='/auth/login/')
def plataforma(request):
    return HttpResponse("plataforma.")




