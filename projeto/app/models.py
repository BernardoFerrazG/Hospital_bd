from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    papel = models.CharField(max_length=50, default='paciente') 
    
    def __str__(self):
        return self.user.username
