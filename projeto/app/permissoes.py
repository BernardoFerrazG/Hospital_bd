"""Controle de acesso por papel (paciente, médico, enfermeiro, administrador).

O usuário do Django é ligado à tabela ``pessoa`` pelo username, que pode ser o
CPF ou o nome cadastrado (o fluxo de cadastro usa o nome).
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Administrador, Enfermeiro, Funcionario, Medico, Paciente, Pessoa

PACIENTE = "paciente"
MEDICO = "medico"
ENFERMEIRO = "enfermeiro"
ADMINISTRADOR = "administrador"


def pessoa_do_usuario(user):
    if not user.is_authenticated:
        return None
    return Pessoa.objects.filter(cpf=user.username).first() or Pessoa.objects.filter(nome=user.username).first()


def papel_da_pessoa(pessoa):
    if pessoa is None:
        return None
    funcionario = Funcionario.objects.filter(fcpf=pessoa).first()
    if funcionario:
        if Administrador.objects.filter(acpf=funcionario).exists():
            return ADMINISTRADOR
        if Medico.objects.filter(mcpf=funcionario).exists():
            return MEDICO
        if Enfermeiro.objects.filter(ecpf=funcionario).exists():
            return ENFERMEIRO
        return None
    if Paciente.objects.filter(pcpf=pessoa).exists():
        return PACIENTE
    return None


def papel_do_usuario(user):
    return papel_da_pessoa(pessoa_do_usuario(user))


def pode_cadastrar_equipe(user, papel):
    """Médicos, enfermeiros e administradores só podem ser cadastrados por um administrador.

    Exceção: enquanto o sistema não tiver nenhum administrador, o primeiro pode se
    cadastrar sozinho (bootstrap da instalação).
    """
    if papel == ADMINISTRADOR and not Administrador.objects.exists():
        return True
    return papel_do_usuario(user) == ADMINISTRADOR


def requer_papel(*papeis):
    """Exige login e que o usuário tenha um dos papéis informados (senão, 403)."""

    def decorador(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if papel_do_usuario(request.user) not in papeis:
                return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
            return view(request, *args, **kwargs)

        return wrapper

    return decorador
