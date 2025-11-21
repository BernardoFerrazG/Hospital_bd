from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Medico
from django.contrib.auth.decorators import login_required


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
        return render(request, "cadastros/cadastro_medico.html", {"pessoa": pessoa})

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


@login_required(login_url='/auth/login/')
def home_med(request):
    return render(request, "home/home_med.html")