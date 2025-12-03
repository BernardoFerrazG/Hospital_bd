from django.db import models

# =============== PESSOA ===============
class Pessoa(models.Model):
    cpf = models.CharField(primary_key=True, max_length=11)
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    senha = models.CharField(max_length=256, null=True)  # você adicionou via ALTER TABLE

    class Meta:
        managed = False
        db_table = 'pessoa'

# =============== FUNCIONARIO ===============
class Funcionario(models.Model):
    fcpf = models.OneToOneField(
        Pessoa,
        primary_key=True,
        on_delete=models.CASCADE,
        db_column='fcpf'
    )
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'funcionario'

class Medico(models.Model):
    crm = models.CharField(primary_key=True, max_length=20)
    mcpf = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        db_column='mcpf'
    )

    class Meta:
        managed = False
        db_table = 'medico'

    def __str__(self):
        return self.crm
    
class Enfermeiro(models.Model):
    coren = models.CharField(primary_key=True, max_length=20, db_column='coren')
    ecpf = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        db_column='ecpf'
    )

    class Meta:
        managed = False
        db_table = 'enfermeiro'

    def __str__(self):
        return self.coren



# =============== ADMINISTRADOR ===============
class Administrador(models.Model):
    acpf = models.OneToOneField(
        Funcionario,
        primary_key=True,
        on_delete=models.CASCADE,
        db_column='acpf'
    )

    class Meta:
        managed = False
        db_table = 'administrador'

# =============== DEPARTAMENTO ===============
class Departamento(models.Model):
    dnome = models.CharField(primary_key=True, max_length=50)
    cpf_administrador = models.OneToOneField(
        Administrador,
        on_delete=models.CASCADE,
        db_column='cpf_administrador'
    )

    class Meta:
        managed = False
        db_table = 'departamento'

class LeitoCirurgico(models.Model):
    numero = models.AutoField(primary_key=True)
    departamento = models.CharField(max_length=50, null=True)
    fenfermeiro = models.CharField(max_length=20, null=True)
    fpaciente = models.CharField(max_length=11, null=True)
    status = models.CharField(max_length=20, default="Disponível")

    class Meta:
        db_table = 'leito_cirurgico'

class LeitoUTI(models.Model):
    numero = models.AutoField(primary_key=True)
    departamento = models.CharField(max_length=50, null=True)
    fenfermeiro = models.CharField(max_length=20, null=True)
    fpaciente = models.CharField(max_length=11, null=True)
    status = models.CharField(max_length=20, default="Disponível")

    class Meta:
        db_table = 'leito_uti'


class Consultorio(models.Model):

    andar = models.IntegerField(primary_key=True)
    numero = models.IntegerField()

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        db_column="departamento",
        null=True,
        blank=True
    )

    fmedico = models.ForeignKey(
        'Medico',
        on_delete=models.SET_NULL,
        db_column="fmedico",
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "consultorio"
        unique_together = (("andar", "numero"),)

    def __str__(self):
        return f"Consultório {self.numero} (Andar {self.andar})"

class SalaCirurgia(models.Model):
    numero = models.AutoField(primary_key=True)  # SERIAL PRIMARY KEY no banco

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="departamento"
    )

    fmedico = models.ForeignKey(
        Medico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="fmedico"
    )

    fenfermeiro = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column="fenfermeiro"
    )  
    # Ou use um ForeignKey para ENFERMEIRO caso você tenha o model

    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "sala_cirurgia"

    def __str__(self):
        return f"Sala {self.numero}"

class MedicoTrabalhaConsultorio(models.Model):
    crm_medico = models.OneToOneField(
        Medico,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='crm_medico'
    )

    andar = models.IntegerField()
    numero = models.IntegerField()

    data_inicio = models.DateField()
    data_fim = models.DateField()

    class Meta:
        managed = False
        db_table = '"MEDICO_TRABALHA_CONSULTORIO"'

class EnfermeiroTrabalhaConsultorio(models.Model):
    coren_enfermeiro = models.OneToOneField(
        Enfermeiro,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='coren_enfermeiro'
    )

    andar = models.IntegerField()
    numero = models.IntegerField()

    data_inicio = models.DateField()
    data_fim = models.DateField()

    class Meta:
        managed = False
        db_table = '"ENFERMEIRO_TRABALHA_CONSULTORIO"'



