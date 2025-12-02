from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Medico, Enfermeiro, Paciente, SalaCirurgia, Cirurgia, LeitoCirurgico, LeitoUTI
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages



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


@login_required(login_url='/login/')
def listar_salas(request):
    """
    Lista somente salas disponíveis e mostra formulário para reservar.
    """
    # só salas com status 'disponivel' (case-insensitive)
    salas = SalaCirurgia.objects.filter(status__iexact='disponivel').order_by('numero')
    enfermeiros = Enfermeiro.objects.all().order_by('ecpf')  # traz todos (para atribuir)
    return render(request, "usuarios/medico/listar_salas.html", {
        "salas": salas,
        "enfermeiros": enfermeiros,
    })


@login_required(login_url='/login/')
def alocar_sala(request):
    """
    POST handler: aloca a sala para o médico logado, cria registro Cirurgia.
    Form fields: sala_numero, data (YYYY-MM-DD), horario (HH:MM), coren (opcional), paciente_pcpf (opcional)
    """
    if request.method != "POST":
        return HttpResponse("Método inválido", status=405)

    sala_numero = request.POST.get("sala_numero")
    data_str = request.POST.get("data")
    horario_str = request.POST.get("horario")
    coren = request.POST.get("coren") or None
    paciente_pcpf = request.POST.get("paciente_pcpf") or None

    if not (sala_numero and data_str and horario_str):
        messages.error(request, "Preencha sala, data e horário.")
        return redirect(reverse("listar_salas"))

    # identifica médico logado
    username = request.user.username
    pessoa = Pessoa.objects.filter(cpf=username).first() or Pessoa.objects.filter(nome=username).first()
    if not pessoa:
        messages.error(request, "Usuário não registrado na tabela Pessoa.")
        return redirect(reverse("listar_salas"))

    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if not funcionario:
        messages.error(request, "Usuário não encontrado como funcionário.")
        return redirect(reverse("listar_salas"))

    medico = Medico.objects.filter(mcpf=funcionario).first()
    if not medico:
        messages.error(request, "Usuário não é um médico.")
        return redirect(reverse("listar_salas"))

    # parse data/horario
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        horario_obj = datetime.strptime(horario_str, "%H:%M").time()
        sala_numero_int = int(sala_numero)
    except Exception:
        messages.error(request, "Formato de data/hora/sala inválido.")
        return redirect(reverse("listar_salas"))

    # checagem simples de conflito: já existe cirurgia com mesma sala/data/horário?
    conflito = Cirurgia.objects.filter(fsala__numero=sala_numero_int, data=data_obj, horario=horario_obj).exists()
    if conflito:
        messages.error(request, "Conflito: já existe cirurgia nessa sala nesse horário.")
        return redirect(reverse("listar_salas"))

    try:
        with transaction.atomic():
            sala = SalaCirurgia.objects.select_for_update().get(numero=sala_numero_int)

            # resolve enfermeiro/paciente se fornecidos
            enfermeiro_obj = None
            paciente_obj = None
            if coren:
                enfermeiro_obj = Enfermeiro.objects.filter(coren=coren).first()
                if not enfermeiro_obj:
                    messages.error(request, "Enfermeiro não encontrado (COREN inválido).")
                    return redirect(reverse("listar_salas"))
            if paciente_pcpf:
                paciente_obj = Paciente.objects.filter(pcpf=paciente_pcpf).first()
                if not paciente_obj:
                    messages.error(request, "Paciente não encontrado (CPF inválido).")
                    return redirect(reverse("listar_salas"))

            # Atualiza sala: atribui médico e (opcional) enfermeiro, marca ocupado
            sala.fmedico = medico
            sala.fenfermeiro = enfermeiro_obj
            sala.status = "ocupado"
            sala.save()

            # cria a cirurgia (registro)
            Cirurgia.objects.create(
                horario=horario_obj,
                data=data_obj,
                fpaciente=paciente_obj,
                fmedico=medico,
                fsala=sala,
                fenfermeiro=enfermeiro_obj
            )
    except SalaCirurgia.DoesNotExist:
        messages.error(request, "Sala não encontrada.")
        return redirect(reverse("listar_salas"))
    except Exception as e:
        messages.error(request, f"Erro ao alocar sala: {e}")
        return redirect(reverse("listar_salas"))

    messages.success(request, f"Cirurgia agendada e sala #{sala_numero_int} reservada.")
    # se tinha paciente, encaminha para alocação de leito (preenchendo querystring),
    # senão volta para listar salas.
    if paciente_pcpf:
        return redirect(f"{reverse('listar_leitos')}?paciente={paciente_pcpf}")
    return redirect(reverse("listar_salas"))



@login_required(login_url='/login/')
def listar_leitos(request):
    """
    Lista leitos cirúrgicos e de UTI disponíveis (status='disponivel') e
    exibe formulário para alocar um leito ao paciente.
    Opcional: receber ?paciente=CPF para pré-preencher.
    """
    leitos_cir = LeitoCirurgico.objects.filter(status__iexact='disponivel').order_by('numero')
    leitos_uti = LeitoUTI.objects.filter(status__iexact='disponivel').order_by('numero')
    paciente_prefill = request.GET.get('paciente')
    return render(request, "usuarios/medico/listar_leitos.html", {
        "leitos_cir": leitos_cir,
        "leitos_uti": leitos_uti,
        "paciente_prefill": paciente_prefill,
    })


@login_required(login_url='/login/')
def alocar_leito(request):
    """
    POST: aloca um leito cirurgico ou UTI para um paciente.
    fields: tipo ('cirurgico'|'uti'), leito_numero, paciente_pcpf, coren (opcional)
    """
    if request.method != "POST":
        return HttpResponse("Método inválido", status=405)

    tipo = request.POST.get("tipo")
    leito_numero = request.POST.get("leito_numero")
    paciente_pcpf = request.POST.get("paciente_pcpf")
    coren = request.POST.get("coren") or None

    if not (tipo and leito_numero and paciente_pcpf):
        return HttpResponse("Preencha tipo, leito e cpf do paciente.", status=400)

    try:
        paciente = Paciente.objects.filter(pcpf=paciente_pcpf).first()
        if not paciente:
            return HttpResponse("Paciente não encontrado.", status=404)

        enfermeiro_obj = None
        if coren:
            enfermeiro_obj = Enfermeiro.objects.filter(coren=coren).first()
            if not enfermeiro_obj:
                return HttpResponse("Enfermeiro não encontrado (COREN inválido).", status=404)

        leito_numero_int = int(leito_numero)
    except Exception:
        return HttpResponse("Dados inválidos.", status=400)

    try:
        with transaction.atomic():
            if tipo == "cirurgico":
                leito = LeitoCirurgico.objects.select_for_update().get(numero=leito_numero_int)
            elif tipo == "uti":
                leito = LeitoUTI.objects.select_for_update().get(numero=leito_numero_int)
            else:
                return HttpResponse("Tipo de leito inválido.", status=400)

            if leito.status and leito.status.lower() == 'ocupado':
                return HttpResponse("Leito já ocupado.", status=400)

            leito.fpaciente = paciente
            if enfermeiro_obj:
                leito.fenfermeiro = enfermeiro_obj
            leito.status = "ocupado"
            leito.save()
    except (LeitoCirurgico.DoesNotExist, LeitoUTI.DoesNotExist):
        return HttpResponse("Leito não encontrado.", status=404)
    except Exception as e:
        return HttpResponse(f"Erro ao alocar leito: {e}", status=500)

    # volta pra lista (ou para a página da cirurgia, se quiser)
    return redirect(reverse("listar_leitos"))