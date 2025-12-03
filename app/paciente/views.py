from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..models import Pessoa, Paciente, Cirurgia, Consulta, Medico
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, date


def cadastro_paciente(request):
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

    cpf_hidden = request.POST.get("cpf", "").strip()
    cpf_confirm = request.POST.get("cpf_confirm", "").strip()

    if not cpf_confirm:
        return HttpResponse("CPF de confirmação é obrigatório.", status=400)

    if cpf_hidden:
        if cpf_confirm != cpf_hidden:
            return HttpResponse("CPF de confirmação não corresponde ao CPF esperado.", status=400)
        cpf = cpf_hidden
    else:
        cpf = cpf_confirm

    try:
        pessoa_obj = Pessoa.objects.get(cpf=cpf)
    except Pessoa.DoesNotExist:
        return HttpResponse("Pessoa não encontrada com esse CPF. Faça primeiro o cadastro inicial.", status=404)

    if Paciente.objects.filter(pcpf=pessoa_obj).exists():
        return HttpResponse("Já existe um paciente cadastrado com esse CPF.", status=400)

    try:
        with transaction.atomic():
            Paciente.objects.create(
                pcpf=pessoa_obj
            )

            if 'cpf' in request.session:
                try:
                    request.session.pop('cpf', None)
                    request.session.save()
                except Exception:
                    pass

    except Exception as e:
        return HttpResponse(f"Erro ao cadastrar paciente: {e}", status=500)

    return redirect(reverse("login"))




@login_required(login_url='/login/')
def home(request):
    """
    Renderiza o Painel do Paciente e carrega o contexto necessário (Pessoa, Médico) 
    para as abas de agendamento.
    """
    username = request.user.username
    
    pessoa = None
    paciente = None
    
    try:
        pessoa = Pessoa.objects.get(cpf=username)
    except Pessoa.DoesNotExist:
        try:
            pessoa = Pessoa.objects.get(nome=username)
        except Pessoa.DoesNotExist:
            pass
    
    if pessoa:
        paciente = Paciente.objects.filter(pcpf=pessoa.cpf).first()
        
    medicos = Medico.objects.all() 
    
    active_tab = request.GET.get('tab', 'resumo')
    
    return render(request, "home/home.html", {
        'paciente': paciente, 
        'medicos': medicos, 
        'pessoa': pessoa,
        'active_tab': active_tab
    })

@login_required(login_url='/login/')
def minha_agenda(request):
    """
    Busca todas as consultas e cirurgias agendadas para o paciente logado que ainda irão acontecer.
    """
    template_name = 'usuarios/paciente/listar_agendamentos.html'

    username = request.user.username
    # 1. Define a data de hoje para o filtro
    hoje = date.today() 

    # 2. Identificar o Usuário/Pessoa
    pessoa = Pessoa.objects.filter(cpf=username).first()
    
    if not pessoa:
        pessoa = Pessoa.objects.filter(nome=username).first()

    if not pessoa:
        messages.error(request, "Usuário não encontrado na base de Pessoas.")
        return redirect('home') 

    # 3. Identificar o Paciente
    paciente = Paciente.objects.filter(pcpf=pessoa.cpf).first()
    
    if not paciente:
        messages.error(request, "Perfil de Paciente não encontrado. Verifique se o cadastro está completo.")
        return redirect('home')

    # 4. Buscar Consultas e Cirurgias FUTURAS (data >= hoje)
    try:
        # Filtra consultas de hoje em diante
        consultas = Consulta.objects.filter(
            fpaciente=paciente,
            data__gte=hoje 
        ).order_by('data', 'horario')
    except Exception as e:
        print(f"Erro ao buscar consultas: {e}")
        consultas = []

    try:
        # Filtra cirurgias de hoje em diante
        cirurgias = Cirurgia.objects.filter(
            fpaciente=paciente,
            data__gte=hoje 
        ).order_by('data', 'horario')
    except Exception as e:
        print(f"Erro ao buscar cirurgias: {e}")
        cirurgias = []

    context = {
        'consultas': consultas,
        'cirurgias': cirurgias,
        'pessoa': pessoa 
    }
    
    return render(request, template_name, context)

@login_required(login_url='/login/')
def consultar_historico(request):
    """
    Busca todas as consultas e cirurgias cuja data é passada (histórico médico).
    """
    template_name = 'usuarios/paciente/historico_medico.html'
    hoje = date.today()
    
    # 1. Identificar o Paciente 
    username = request.user.username
    pessoa = Pessoa.objects.filter(cpf=username).first()
    if not pessoa:
        pessoa = Pessoa.objects.filter(nome=username).first()
    
    if not pessoa:
        messages.error(request, "Usuário não encontrado.")
        return redirect('home')

    paciente = Paciente.objects.filter(pcpf=pessoa.cpf).first()
    if not paciente:
        messages.error(request, "Perfil de Paciente não encontrado.")
        return redirect('home')

    # 2. BUSCAR HISTÓRICO
    consultas_passadas = Consulta.objects.filter(
        fpaciente=paciente,
        data__lte=hoje 
    ).order_by('-data', '-horario') 

    # Cirurgias passadas 
    cirurgias_passadas = Cirurgia.objects.filter(
        fpaciente=paciente,
        data__lte=hoje
    ).order_by('-data', '-horario')
    
    context = {
        'consultas_passadas': consultas_passadas,
        'cirurgias_passadas': cirurgias_passadas,
        'pessoa': pessoa,
    }
    
    return render(request, template_name, context)

@login_required(login_url='/login/')
def marcar_consulta(request):
    username = request.user.username
    
    try:
        pessoa = Pessoa.objects.get(cpf=username)
    except Pessoa.DoesNotExist:
        try:
            pessoa = Pessoa.objects.get(nome=username)
        except Pessoa.DoesNotExist:
            messages.error(request, "Usuário não encontrado. O cadastro é obrigatório.")
            return redirect('home')
    
    try:
        paciente = Paciente.objects.get(pcpf=pessoa.cpf)
    except Paciente.DoesNotExist:
        messages.error(request, "Perfil de paciente incompleto.")
        return redirect('home')

    medicos = Medico.objects.all()

    if request.method == "POST":
        crm = request.POST.get("fmedico_crm")
        data_str = request.POST.get("data")
        horario_str = request.POST.get("horario")

        if not all([crm, data_str, horario_str]):
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            return redirect(reverse('marcar_consulta')) 

        try:
            medico = Medico.objects.get(crm=crm)
            data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
            horario_obj = datetime.strptime(horario_str, "%H:%M").time()
            
            andar_cons = 1
            numero_cons = 100 
            
            with transaction.atomic():
                consulta, created = Consulta.objects.get_or_create(
                    data=data_obj,
                    horario=horario_obj,
                    fpaciente=paciente,
                    fmedico=medico,
                    defaults={
                        'andar': andar_cons,
                        'numero': numero_cons
                    }
                )
            
            if not created:
                messages.warning(request, 
                                 f"Já existe uma consulta agendada com o Dr(a). {medico.mcpf.fcpf.nome} em {data_str} às {horario_str}. Escolha outro horário.")
                return redirect('minha_agenda')

            messages.success(request, f"Consulta agendada com sucesso para {data_str}.")
            return redirect('minha_agenda')

        except Exception as e:
            messages.error(request, f"Erro ao agendar consulta: {e}")
            return redirect(reverse('marcar_consulta'))
            
    return render(request, 'usuarios/paciente/marcar_consulta.html', {
        'pessoa': pessoa,
        'medicos': medicos,
    })

@login_required(login_url='/login/')
def marcar_cirurgia(request):
    username = request.user.username
    
    try:
        pessoa = Pessoa.objects.get(cpf=username)
    except Pessoa.DoesNotExist:
        try:
            pessoa = Pessoa.objects.get(nome=username)
        except Pessoa.DoesNotExist:
            messages.error(request, "Usuário não encontrado. O cadastro é obrigatório.")
            return redirect('home')
    
    try:
        paciente = Paciente.objects.get(pcpf=pessoa.cpf)
    except Paciente.DoesNotExist:
        messages.error(request, "Perfil de paciente incompleto.")
        return redirect('home')

    medicos = Medico.objects.all() 

    if request.method == "POST":
        crm = request.POST.get("fmedico_crm")
        procedimento = request.POST.get("procedimento")
        observacoes = request.POST.get("observacoes")

        if not all([crm, procedimento]):
            messages.error(request, "Preencha o médico e o procedimento.")
            return redirect(reverse('marcar_cirurgia'))

        try:
            medico = Medico.objects.get(crm=crm)
            
            with transaction.atomic():
                cirurgia, created = Cirurgia.objects.get_or_create(
                    fpaciente=paciente,
                    fmedico=medico,
                    defaults={
                        # Data, Horario, Sala ficam NULL para o Médico agendar.
                    }
                )
            
            if not created:
                 messages.warning(request, f"Uma solicitação de cirurgia idêntica para o(a) Dr(a). {medico.mcpf.fcpf.nome} já está pendente. Aguarde a confirmação.")
                 return redirect('minha_agenda')

            messages.success(request, f"Solicitação de Cirurgia para '{procedimento}' enviada. Aguarde a confirmação.")
            return redirect('minha_agenda')

        except Exception as e:
            messages.error(request, f"Erro ao solicitar cirurgia: {e}")
            return redirect(reverse('marcar_cirurgia'))

    return render(request, 'usuarios/paciente/marcar_cirurgia.html', {
        'pessoa': pessoa,
        'medicos': medicos,
    })