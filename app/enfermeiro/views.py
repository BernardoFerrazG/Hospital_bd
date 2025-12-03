from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Enfermeiro, Departamento, FuncionarioTrabalhaEm
from django.contrib.auth.decorators import login_required






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
    from django.contrib.auth.models import User

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

        # tenta inferir quem fez a alocação a partir do departamento (campo cpf_administrador)
        admin_username = "—"
        if a.nome_departamento and getattr(a.nome_departamento, 'cpf_administrador', None):
            cpf_admin = a.nome_departamento.cpf_administrador
            admin_pessoa = Pessoa.objects.filter(cpf=cpf_admin).first()
            if admin_pessoa:
                admin_user = User.objects.filter(username=admin_pessoa.nome).first()
                if admin_user:
                    admin_username = admin_user.username
                else:
                    admin_username = admin_pessoa.nome
            else:
                admin_username = cpf_admin

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