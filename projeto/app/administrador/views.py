from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Administrador, Departamento, FuncionarioTrabalhaEm
from django.contrib.auth.decorators import login_required



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
        return render(request, "cadastros/cadastro_admin.html", {"pessoa": pessoa})

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



@login_required(login_url='/auth/login/')
def home_admin(request):
    return render(request, "home/home_admin.html")

@login_required(login_url='/auth/login/')
def alocar(request):
    if request.method == "GET":
        funcionarios = Funcionario.objects.all()
        departamentos = Departamento.objects.all()
        return render(request, "alocar/alocar_funcionario.html", {
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