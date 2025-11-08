from django.db import models

# Create your models here.
# serve para criar o que vamos usar nesse app, as informações que vamos armazenar no banco de dados

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.TextField(max_length=100)
    idade = models.IntegerField()