from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Paciente
from ..permissoes import PACIENTE, requer_papel


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
        return render(request, "cadastros/cadastro_paciente.html", {"pessoa": pessoa})

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




@requer_papel(PACIENTE)
def home(request):
    return render(request, "home/home.html")

