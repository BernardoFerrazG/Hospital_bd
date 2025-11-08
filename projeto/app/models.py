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

