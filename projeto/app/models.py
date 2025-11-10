from django.db import models


class Pessoa(models.Model):
    cpf = models.CharField(primary_key=True, max_length=11)
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    data_nascimento = models.DateField()

    class Meta:
        managed = False  # Django não cria nem altera a tabela
        db_table = 'pessoa'  # nome exato no banco



class Funcionario(models.Model):
    fcpf = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        db_column='fcpf',
        primary_key=True
    )
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'funcionario'



class Medico(models.Model):
    crm = models.CharField(primary_key=True, max_length=20)
    mcpf = models.OneToOneField(
        Funcionario, to_field='fcpf',
        on_delete=models.CASCADE,
        db_column='mcpf'
    )

    class Meta:
        managed = False
        db_table = 'medico'
        
        
## Modelo para Departamento e Alocação de Funcionários
        
class Departamento(models.Model):
    dnome = models.CharField(primary_key=True, max_length=50)
    cpf_administrador = models.CharField(max_length=11, unique=True)

    class Meta:
        managed = False
        db_table = 'departamento'


class FuncionarioTrabalhaEm(models.Model):
    cpf_funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        db_column='cpf_funcionario',
        primary_key=True
    )
    nome_departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        db_column='nome_departamento'
    )
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'funcionario_trabalha_em'
        