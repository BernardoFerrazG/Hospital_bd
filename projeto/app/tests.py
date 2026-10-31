from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Administrador, Enfermeiro, Funcionario, Medico, Paciente, Pessoa
from .permissoes import ADMINISTRADOR, ENFERMEIRO, MEDICO, PACIENTE, papel_do_usuario

SENHA = "senha-de-teste-123"


def cria_pessoa(cpf, nome):
    pessoa = Pessoa.objects.create(cpf=cpf, nome=nome, sexo="F", telefone="", email="", data_nascimento=date(1990, 1, 1))
    User.objects.create_user(username=nome, password=SENHA)
    return pessoa


def cria_funcionario(cpf, nome):
    return Funcionario.objects.create(fcpf=cria_pessoa(cpf, nome), salario=0, horas_trabalhadas=0)


class PapelDoUsuarioTests(TestCase):
    def setUp(self):
        Paciente.objects.create(pcpf=cria_pessoa("1", "paciente"))
        Medico.objects.create(crm="CRM1", mcpf=cria_funcionario("2", "medico"))
        Enfermeiro.objects.create(coren="COREN1", ecpf=cria_funcionario("3", "enfermeiro"))
        Administrador.objects.create(acpf=cria_funcionario("4", "admin"))

    def test_identifica_cada_papel(self):
        esperado = {"paciente": PACIENTE, "medico": MEDICO, "enfermeiro": ENFERMEIRO, "admin": ADMINISTRADOR}
        for username, papel in esperado.items():
            self.assertEqual(papel_do_usuario(User.objects.get(username=username)), papel)


class ControleDeAcessoTests(TestCase):
    def setUp(self):
        Paciente.objects.create(pcpf=cria_pessoa("1", "paciente"))
        Administrador.objects.create(acpf=cria_funcionario("4", "admin"))

    def test_anonimo_e_redirecionado_para_o_login(self):
        for rota in ["home", "home_admin", "home_med", "home_enf", "listar_salas", "alocar"]:
            resposta = self.client.get(reverse(rota))
            self.assertEqual(resposta.status_code, 302, rota)
            self.assertTrue(resposta["Location"].startswith(reverse("login")), rota)

    def test_paciente_nao_acessa_paginas_de_outros_papeis(self):
        self.client.login(username="paciente", password=SENHA)
        for rota in ["home_admin", "alocar", "home_med", "listar_salas", "listar_leitos", "home_enf"]:
            self.assertEqual(self.client.get(reverse(rota)).status_code, 403, rota)

    def test_paciente_acessa_a_propria_home(self):
        self.client.login(username="paciente", password=SENHA)
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_admin_acessa_painel(self):
        self.client.login(username="admin", password=SENHA)
        self.assertEqual(self.client.get(reverse("home_admin")).status_code, 200)


class CadastroDeEquipeTests(TestCase):
    def dados(self, cpf, nome, papel):
        return {"nome": nome, "cpf": cpf, "senha": SENHA, "papel": papel, "sexo": "M",
                "telefone": "", "email": "", "data_nascimento": "1990-01-01"}

    def test_primeiro_administrador_pode_se_cadastrar(self):
        resposta = self.client.post(reverse("cadastro"), self.dados("10", "primeiro", "admin"))
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(Pessoa.objects.filter(cpf="10").exists())

    def test_publico_nao_cadastra_administrador_quando_ja_existe_um(self):
        Administrador.objects.create(acpf=cria_funcionario("4", "admin"))
        resposta = self.client.post(reverse("cadastro"), self.dados("11", "intruso", "admin"))
        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Pessoa.objects.filter(cpf="11").exists())

    def test_publico_nao_cadastra_medico(self):
        Administrador.objects.create(acpf=cria_funcionario("4", "admin"))
        self.assertEqual(self.client.post(reverse("cadastro"), self.dados("12", "falso", "medico")).status_code, 403)
        self.assertEqual(self.client.get(reverse("cadastro_medico")).status_code, 403)
        self.assertEqual(self.client.get(reverse("cadastro_admin")).status_code, 403)

    def test_admin_cadastra_medico(self):
        Administrador.objects.create(acpf=cria_funcionario("4", "admin"))
        self.client.login(username="admin", password=SENHA)
        resposta = self.client.post(reverse("cadastro"), self.dados("13", "doutora", "medico"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("cadastro_medico"), resposta["Location"])

    def test_paciente_pode_se_cadastrar(self):
        resposta = self.client.post(reverse("cadastro"), self.dados("14", "novo", "paciente"))
        self.assertEqual(resposta.status_code, 302)

    def test_papel_invalido_nao_cria_registros(self):
        resposta = self.client.post(reverse("cadastro"), self.dados("15", "x", "hacker"))
        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(Pessoa.objects.filter(cpf="15").exists())
        self.assertFalse(User.objects.filter(username="x").exists())
