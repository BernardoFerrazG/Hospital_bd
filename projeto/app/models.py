from django.db import models


class Pessoa(models.Model):
    cpf = models.CharField(primary_key=True, max_length=11)
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    senha = models.CharField(max_length=255, blank=True, null=True)

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
        
class Enfermeiro(models.Model):
    coren = models.CharField(primary_key=True, max_length=20)
    ecpf = models.OneToOneField(
        Funcionario,
        to_field='fcpf',
        on_delete=models.CASCADE,
        db_column='ecpf'
    )

    class Meta:
        managed = False
        db_table = 'enfermeiro'

    def __str__(self):
        return f"{self.coren} - {self.ecpf_id}"


class Administrador(models.Model):
    acpf = models.OneToOneField(
        Funcionario,
        to_field='fcpf',
        on_delete=models.CASCADE,
        db_column='acpf',
        primary_key=True
    )

    class Meta:
        managed = False
        db_table = 'administrador'

    def __str__(self):
        return f"Administrador (CPF func): {self.acpf_id}"


class Paciente(models.Model):
    pcpf = models.OneToOneField(
        Pessoa,
        to_field='cpf',
        on_delete=models.CASCADE,
        db_column='pcpf',
        primary_key=True
    )

    class Meta:
        managed = False
        db_table = 'paciente'

    def __str__(self):
        return f"Paciente (CPF): {self.pcpf_id}"


        
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
        


class SalaCirurgia(models.Model):
    numero = models.AutoField(primary_key=True)   # SERIAL
    departamento = models.ForeignKey(
        'Departamento', db_column='departamento',
        on_delete=models.SET_NULL, null=True, blank=True, to_field='dnome'
    )

    fmedico = models.ForeignKey(
        "Medico",
        to_field="crm",
        db_column="fmedico",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fenfermeiro = models.ForeignKey(
        "Enfermeiro",
        to_field="coren",
        db_column="fenfermeiro",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    status = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "sala_cirurgia"


class LeitoCirurgico(models.Model):
    numero = models.AutoField(primary_key=True)  # SERIAL
    departamento = models.CharField(max_length=50, null=True, blank=True)

    fenfermeiro = models.ForeignKey(
        "Enfermeiro",
        to_field="coren",
        db_column="fenfermeiro",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fpaciente = models.ForeignKey(
        "Paciente",
        to_field="pcpf",
        db_column="fpaciente",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    status = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "leito_cirurgico"


class LeitoUTI(models.Model):
    numero = models.AutoField(primary_key=True)  # SERIAL
    departamento = models.CharField(max_length=50, null=True, blank=True)

    fenfermeiro = models.ForeignKey(
        "Enfermeiro",
        to_field="coren",
        db_column="fenfermeiro",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fpaciente = models.ForeignKey(
        "Paciente",
        to_field="pcpf",
        db_column="fpaciente",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    status = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "leito_uti"


class Cirurgia(models.Model):
    nmr_cirurgia = models.AutoField(primary_key=True)
    horario = models.TimeField(null=True, blank=True)
    data = models.DateField(null=True, blank=True)

    fpaciente = models.ForeignKey(
        "Paciente",
        to_field="pcpf",
        db_column="fpaciente",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fmedico = models.ForeignKey(
        "Medico",
        to_field="crm",
        db_column="fmedico",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fsala = models.ForeignKey(
        "SalaCirurgia",
        to_field="numero",
        db_column="fsala",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fenfermeiro = models.ForeignKey(
        "Enfermeiro",
        to_field="coren",
        db_column="fenfermeiro",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        managed = False
        db_table = "cirurgia"


class Consulta(models.Model):
    nmr_consulta = models.AutoField(primary_key=True)
    horario = models.TimeField(null=True, blank=True)
    data = models.DateField(null=True, blank=True)

    fpaciente = models.ForeignKey(
        "Paciente",
        to_field="pcpf",
        db_column="fpaciente",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    fmedico = models.ForeignKey(
        "Medico",
        to_field="crm",
        db_column="fmedico",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    andar = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "consulta"

    def __str__(self):
        paciente_nome = self.fpaciente.pcpf.nome if self.fpaciente and self.fpaciente.pcpf else "—"
        return f"{self.data} {self.horario} — {paciente_nome} — consultório {self.andar}/{self.numero}"
