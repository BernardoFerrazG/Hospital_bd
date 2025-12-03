from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Funcionario, Medico, Enfermeiro, Paciente, SalaCirurgia, Cirurgia, LeitoCirurgico, LeitoUTI, Consulta
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
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

    salas = SalaCirurgia.objects.order_by('numero')
    enfermeiros = Enfermeiro.objects.all().order_by('ecpf')

    cirurgias = Cirurgia.objects.order_by('data', 'horario')[:8]

    return render(request, "usuarios/medico/listar_salas.html", {
        "salas": salas,
        "enfermeiros": enfermeiros,
        "cirurgias": cirurgias,
    })



@login_required(login_url='/login/')
def alocar_sala(request):
    """
    POST: aloca a sala, cria registro Cirurgia.
    Regras:
      - não permite mais de UMA cirurgia por SALA na MESMA DATA;
      - não permite alocar se sala.status == 'ocupado' (case-insensitive).
    Aceita o campo opcional 'needs_leito' (checkbox).
    """
    if request.method != "POST":
        return HttpResponse("Método inválido", status=405)

    sala_numero = request.POST.get("sala_numero")
    data_str = request.POST.get("data")
    horario_str = request.POST.get("horario")
    coren = request.POST.get("coren") or None
    paciente_pcpf = request.POST.get("paciente_pcpf") or None

    # checkbox indicando necessidade de leito
    needs_leito_raw = request.POST.get("needs_leito")
    needs_leito = False
    if needs_leito_raw:
        needs_leito = str(needs_leito_raw).lower() in ("on", "1", "true", "yes")

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

    try:
        with transaction.atomic():
            sala = SalaCirurgia.objects.select_for_update().get(numero=sala_numero_int)

            # não permite alocar se a sala já estiver marcada como ocupada
            if sala.status and str(sala.status).strip().lower() == "ocupado":
                messages.error(request, "Esta sala já está marcada como ocupada e não pode receber outra cirurgia.")
                return redirect(reverse("listar_salas"))

            # checagem estrita: não permita outra cirurgia para a mesma sala na mesma DATA
            conflito_data = Cirurgia.objects.filter(fsala__numero=sala_numero_int, data=data_obj).exists()
            if conflito_data:
                messages.error(request, "Conflito: já existe uma cirurgia agendada para esta sala nessa data.")
                return redirect(reverse("listar_salas"))

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

            # marcar sala e criar cirurgia
            sala.fmedico = medico
            sala.fenfermeiro = enfermeiro_obj
            sala.status = "ocupado"
            sala.save()

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

    # Só redireciona para alocação de leito se o médico marcou explicitamente e há paciente informado.
    if needs_leito and paciente_pcpf:
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


@login_required(login_url='/login/')
def listar_consultas(request):
    """
    Lista as consultas do médico logado para uma data.
    Por padrão usa hoje; aceita ?date=YYYY-MM-DD para ver outra data.
    Mostra horário, paciente e consultório (andar/numero).
    """
    # identifica médico a partir do usuário (mesma mecânica que você já usa)
    username = request.user.username
    pessoa = Pessoa.objects.filter(cpf=username).first() or Pessoa.objects.filter(nome=username).first()
    if not pessoa:
        messages.error(request, "Usuário não registrado na tabela Pessoa.")
        return redirect(reverse("home_med"))

    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if not funcionario:
        messages.error(request, "Usuário não encontrado como funcionário.")
        return redirect(reverse("home_med"))

    medico = Medico.objects.filter(mcpf=funcionario).first()
    if not medico:
        messages.error(request, "Usuário não é um médico.")
        return redirect(reverse("home_med"))

    # data desejada (querystring opcional)
    date_str = request.GET.get('date')
    if date_str:
        try:
            data_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            data_obj = date.today()
            messages.warning(request, "Formato de data inválido; mostrando hoje.")
    else:
        data_obj = date.today()

    consultas = Consulta.objects.filter(fmedico=medico, data=data_obj).order_by('horario')

    return render(request, "usuarios/medico/listar_consultas.html", {
        "consultas": consultas,
        "data": data_obj,
    })

@login_required(login_url='/auth/login/')
def gerenciar_salas(request):
    # identifica médico
    username = request.user.username
    pessoa = Pessoa.objects.filter(cpf=username).first() or Pessoa.objects.filter(nome=username).first()
    if not pessoa:
        messages.error(request, "Usuário não está registrado como Pessoa.")
        return redirect(reverse("home_med"))

    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if not funcionario:
        messages.error(request, "Usuário não encontrado como funcionário.")
        return redirect(reverse("home_med"))

    medico = Medico.objects.filter(mcpf=funcionario).first()
    if not medico:
        messages.error(request, "Usuário não é um médico.")
        return redirect(reverse("home_med"))

    # salas alocadas a este médico (ordenadas)
    salas = SalaCirurgia.objects.filter(fmedico=medico).order_by('numero')

    # para cada sala, pegar próximas cirurgias futuras (data >= hoje)
    today = date.today()
    salas_with_cir = []
    for sala in salas:
        cir_list = list(Cirurgia.objects.filter(fsala=sala, data__gte=today).order_by('data', 'horario')[:5])
        salas_with_cir.append((sala, cir_list))

    # --- CORREÇÃO PRINCIPAL aqui ---
    # pegar ids de pacientes que aparecem nas cirurgias do médico (fpaciente_id)
    paciente_ids = Cirurgia.objects.filter(fmedico=medico).values_list('fpaciente_id', flat=True)
    # filtra os pacientes por id (evita usar nomes de campo incorretos como 'cpf')
    paciente_qs = Paciente.objects.filter(pk__in=[pid for pid in paciente_ids if pid])

    # leitos ocupados relacionados a esses pacientes
    leitos_cir_ocup = LeitoCirurgico.objects.filter(status__iexact='ocupado', fpaciente__in=paciente_qs).order_by('numero')
    leitos_uti_ocup = LeitoUTI.objects.filter(status__iexact='ocupado', fpaciente__in=paciente_qs).order_by('numero')

    return render(request, "usuarios/medico/gerenciar_salas.html", {
        "salas_with_cir": salas_with_cir,
        "leitos_cir_ocup": leitos_cir_ocup,
        "leitos_uti_ocup": leitos_uti_ocup,
    })



@login_required(login_url='/auth/login/')
def desalocar_sala(request):
    """
    Form esperado: POST com campo 'sala_numero' (número da sala) e checkbox 'cancel_cirurgias' (opcional).
    Se cancelar cirurgias, remove cirurgias futuras daquela sala (apenas > hoje).
    """
    sala_numero = request.POST.get("sala_numero")
    cancel = request.POST.get("cancel_cirurgias")  # 'on' se marcado

    if not sala_numero:
        messages.error(request, "Número da sala ausente.")
        return redirect(reverse("gerenciar_salas"))

    try:
        sala_num = int(sala_numero)
    except ValueError:
        messages.error(request, "Número da sala inválido.")
        return redirect(reverse("gerenciar_salas"))

    # confirma médico logado (mesma lógica sua)
    username = request.user.username
    pessoa = Pessoa.objects.filter(cpf=username).first() or Pessoa.objects.filter(nome=username).first()
    if not pessoa:
        messages.error(request, "Usuário não cadastrado como Pessoa.")
        return redirect(reverse("gerenciar_salas"))

    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if not funcionario:
        messages.error(request, "Usuário não é funcionário.")
        return redirect(reverse("gerenciar_salas"))

    medico = Medico.objects.filter(mcpf=funcionario).first()
    if not medico:
        messages.error(request, "Usuário não é médico.")
        return redirect(reverse("gerenciar_salas"))

    try:
        with transaction.atomic():
            sala = SalaCirurgia.objects.select_for_update().get(numero=sala_num)

            # só permitir desalocar se a sala estiver atribuída ao médico logado
            if sala.fmedico != medico:
                messages.error(request, "Você não pode liberar esta sala (não está atribuída a você).")
                return redirect(reverse("gerenciar_salas"))

            # libera a sala (desassocia médico/enfermeiro e marca disponível)
            sala.fmedico = None
            sala.fenfermeiro = None
            sala.status = "disponivel"
            sala.save()

            # se pediu cancelar cirurgias futuras, elimina registros de Cirurgia com data >= hoje
            if cancel:
                hoje = date.today()
                deleted_count, _ = Cirurgia.objects.filter(fsala=sala, data__gte=hoje).delete()
                # .delete() já remove relacionamentos; cuidado com cascades se tiver
                if deleted_count:
                    messages.info(request, f"{deleted_count} cirurgias futuras canceladas.")
    except SalaCirurgia.DoesNotExist:
        messages.error(request, "Sala não encontrada.")
        return redirect(reverse("gerenciar_salas"))
    except Exception as e:
        messages.error(request, f"Erro ao liberar sala: {e}")
        return redirect(reverse("gerenciar_salas"))

    messages.success(request, f"Sala #{sala_num} liberada.")
    return redirect(reverse("gerenciar_salas"))


@login_required(login_url='/auth/login/')
def liberar_leito(request):
    if request.method != "POST":
        return HttpResponse("Método inválido", status=405)

    tipo = request.POST.get("tipo")
    leito_numero = request.POST.get("leito_numero")

    if not (tipo and leito_numero):
        messages.error(request, "Dados incompletos para liberar leito.")
        return redirect(reverse("gerenciar_salas"))

    try:
        leito_num = int(leito_numero)
    except ValueError:
        messages.error(request, "Número do leito inválido.")
        return redirect(reverse("gerenciar_salas"))

    try:
        with transaction.atomic():
            if tipo == "cirurgico":
                leito = LeitoCirurgico.objects.select_for_update().get(numero=leito_num)
            elif tipo == "uti":
                leito = LeitoUTI.objects.select_for_update().get(numero=leito_num)
            else:
                messages.error(request, "Tipo de leito inválido.")
                return redirect(reverse("gerenciar_salas"))

            # limpa vínculo e marca disponível
            leito.fpaciente = None
            leito.fenfermeiro = None
            leito.status = "disponivel"
            leito.save()

    except (LeitoCirurgico.DoesNotExist, LeitoUTI.DoesNotExist):
        messages.error(request, "Leito não encontrado.")
        return redirect(reverse("gerenciar_salas"))
    except Exception as e:
        messages.error(request, f"Erro ao liberar leito: {e}")
        return redirect(reverse("gerenciar_salas"))

    messages.success(request, f"Leito #{leito_num} liberado.")
    return redirect(reverse("gerenciar_salas"))
