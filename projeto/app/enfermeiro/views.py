from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Enfermeiro
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
    return render(request, "home/home_enf.html")


def enfermeiro_alocacoes(request):
    return render(request, "alocar/enfermeiro_alocacoes.html")
