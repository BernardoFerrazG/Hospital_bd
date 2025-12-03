from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from django.contrib.auth.models import User
from ..models import Pessoa, Funcionario, Enfermeiro, Departamento, FuncionarioTrabalhaEm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as login_django, get_user_model





def login_enfermeiro(request):
    if request.method == "GET":
        return render(request, "login/login_enfermeiro.html")
    
    # POST - processar login
    nome = request.POST.get("nome", "").strip()
    senha = request.POST.get("senha", "").strip()
    coren = request.POST.get("coren", "").strip()
    
    if not (nome and senha and coren):
        return HttpResponse("Campos obrigatórios: nome, senha e COREN.", status=400)
    
    # Autenticar usuário
    user = authenticate(username=nome, password=senha)
    if not user:
        return HttpResponse("Credenciais inválidas (nome ou senha incorretos).", status=401)
    
    # Verificar se o usuário autenticado é um enfermeiro com o COREN fornecido
    try:
        # Tentar encontrar a Pessoa associada (por CPF ou nome)
        pessoa = Pessoa.objects.filter(cpf=nome).first()
        if not pessoa:
            pessoa = Pessoa.objects.filter(nome=nome).first()
        
        if not pessoa:
            return HttpResponse("Usuário autenticado, mas sem registro de pessoa.", status=404)
        
        # Verificar se é um funcionário
        funcionario = Funcionario.objects.get(fcpf=pessoa)
        
        # Verificar se é enfermeiro com o COREN correto
        enfermeiro = Enfermeiro.objects.get(ecpf=funcionario, coren=coren)
        
        # Se chegou aqui, tudo está correto - fazer login
        login_django(request, user)
        return redirect(reverse("home_enf"))
        
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada.", status=404)
    except Funcionario.DoesNotExist:
        return HttpResponse("Usuário não é um funcionário registrado.", status=403)
    except Enfermeiro.DoesNotExist:
        return HttpResponse("COREN não encontrado ou não corresponde a este usuário.", status=403)


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
        return render(request, "cadastros/cadastro_enfermeiro.html", {"pessoa": pessoa})

    # POST
    coren = request.POST.get("coren", "").strip()
    cpf_hidden = request.POST.get("cpf", "").strip()
    cpf_confirm = request.POST.get("cpf_confirm", "").strip()
    nome = request.POST.get("nome", "").strip()
    senha = request.POST.get("senha", "").strip()

    if not (coren and cpf_confirm and senha):
        return HttpResponse("Campos obrigatórios: COREN, CPF e Senha.", status=400)

    # Decide o CPF real
    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    # Valida COREN único
    if Enfermeiro.objects.filter(coren=coren).exists():
        return HttpResponse("COREN já cadastrado.", status=400)

    # Tenta obter Pessoa; se não existir e nome foi fornecido, cria automaticamente
    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        if not nome:
            return HttpResponse("Pessoa não encontrada. Por favor, forneça o nome para criar o registro.", status=404)
        
        # Validar duplicatas antes de criar
        if User.objects.filter(username=nome).exists():
            return HttpResponse("Nome de usuário já existe.", status=400)
        
        # Cria pessoa automaticamente se nome foi fornecido
        try:
            pessoa_obj = Pessoa.objects.create(
                cpf=cpf,
                nome=nome,
                sexo="",
                telefone="",
                email="",
                data_nascimento=None
            )
        except Exception as e:
            return HttpResponse(f"Erro ao criar pessoa: {e}", status=500)

    try:
        with transaction.atomic():
            # Criar Funcionario se não existir
            func, criado = Funcionario.objects.get_or_create(
                fcpf=pessoa_obj,
                defaults={
                    "salario": 0,
                    "horas_trabalhadas": 0
                }
            )

            # Criar usuário Django se não existir (apenas se foi criada nova Pessoa)
            if not User.objects.filter(username=pessoa_obj.nome).exists():
                User.objects.create_user(
                    username=pessoa_obj.nome,
                    email=pessoa_obj.email or "",
                    password=senha
                )

            # Criar o enfermeiro
            Enfermeiro.objects.create(
                coren=coren,
                ecpf=func
            )

            # Limpar CPF da sessão se existir
            if 'cpf' in request.session:
                try:
                    request.session.pop('cpf', None)
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar enfermeiro: {e}", status=500)

    # Redirecionar para login do enfermeiro após sucesso
    return redirect(reverse("login_enfermeiro"))



@login_required(login_url='/auth/login/')
def home_enf(request):
    nome_user = request.user.username  
    pessoa = Pessoa.objects.get(nome=nome_user)
    funcionario = Funcionario.objects.get(fcpf=pessoa.cpf)
    enfermeiro = Enfermeiro.objects.get(ecpf=funcionario)

    return render(request, "home/home_enf.html", {
        "enfermeiro": enfermeiro
    })


@login_required(login_url='/auth/login/')
def enfermeiro_alocacoes(request):
    # Monta lista de alocações para o enfermeiro logado compatível com o template
    from types import SimpleNamespace

    # Use the configured user model
    User = get_user_model()

    # Tenta encontrar a Pessoa associada ao usuário (mesma lógica do login)
    username = request.user.username if request.user and request.user.is_authenticated else None
    pessoa = None
    if username:
        pessoa = Pessoa.objects.filter(cpf=username).first()
        if not pessoa:
            pessoa = Pessoa.objects.filter(nome=username).first()

    if not pessoa:
        return HttpResponse("Pessoa vinculada ao usuário não encontrada.", status=404)

    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if not funcionario:
        return HttpResponse("Funcionário não encontrado.", status=404)

    # verifica se é enfermeiro
    try:
        Enfermeiro.objects.get(ecpf=funcionario)
    except Enfermeiro.DoesNotExist:
        return HttpResponse("Nenhum enfermeiro vinculado a esse funcionário.", status=403)

    # Busca alocações (aqui usamos FuncionarioTrabalhaEm, que no modelo atual é one-to-one;
    # ainda assim montamos uma lista para o template que espera um iterável)
    alocs_qs = FuncionarioTrabalhaEm.objects.filter(cpf_funcionario=funcionario)

    alocacoes = []
    for a in alocs_qs:
        # local esperado pelo template: objeto com atributo `nome`
        local_nome = a.nome_departamento.dnome if a.nome_departamento else None
        local = SimpleNamespace(nome=local_nome)

        # tenta inferir quem fez a alocação com múltiplos fallbacks
        admin_username = "—"

        # 1) Se o departamento tem um cpf_administrador, preferimos encontrá-lo
        if a.nome_departamento and getattr(a.nome_departamento, 'cpf_administrador', None):
            cpf_admin = a.nome_departamento.cpf_administrador
            # primeiro, veja se existe um User com username igual ao CPF (username pode ser CPF em alguns fluxos)
            admin_user = User.objects.filter(username=cpf_admin).first()
            if admin_user:
                admin_username = admin_user.username
            else:
                # tenta mapear CPF -> Pessoa -> User (username == pessoa.nome)
                admin_pessoa = Pessoa.objects.filter(cpf=cpf_admin).first()
                if admin_pessoa:
                    admin_user2 = User.objects.filter(username=admin_pessoa.nome).first()
                    if admin_user2:
                        admin_username = admin_user2.username
                    else:
                        admin_username = admin_pessoa.nome
                else:
                    admin_username = cpf_admin
        else:
            # 2) Sem cpf_administrador, tente heurísticas baseadas no próprio funcionário/pessoa
            # a) usuário com username == CPF do funcionário
            func_cpf = funcionario.fcpf_id if hasattr(funcionario, 'fcpf_id') else None
            if func_cpf:
                user_by_cpf = User.objects.filter(username=func_cpf).first()
                if user_by_cpf:
                    admin_username = user_by_cpf.username
            # b) usuário com username == nome da pessoa
            if admin_username == "—":
                user_by_name = User.objects.filter(username=pessoa.nome).first()
                if user_by_name:
                    admin_username = user_by_name.username

        alocado_por = SimpleNamespace(usuario=SimpleNamespace(username=admin_username))

        alocacoes.append(
            SimpleNamespace(
                local=local,
                data_inicio=a.data_inicio,
                data_fim=a.data_fim,
                alocado_por=alocado_por,
            )
        )

    return render(request, "alocar/enfermeiro_alocacoes.html", {"alocacoes": alocacoes})