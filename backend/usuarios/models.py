from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Usuario(models.Model):
    user=models.OneToOneField(User, on_delete=models.RESTRICT, related_name='usuario')
    nombre=models.CharField(max_length=200)
    apellido1=models.CharField(max_length=200)
    apellido2=models.CharField(max_length=200, null=True, blank=True)
    dni=models.CharField(max_length=9, unique=True)

    ROL_OPTIONS=(
        ('gestor', 'gestor'),
        ('presidente', 'presidente'),
        ('propietario', 'propietario'),
        ('vicepresidente', 'vicepresidente'),
        ('secretario', 'secretario'),
    )

    rol=models.CharField(max_length=30, choices=ROL_OPTIONS, default='propietario')
    telefono=models.CharField(max_length=200, null=True, blank=True)
    email=models.EmailField(null=True, blank=True)
    moroso=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre}, {self.apellido1}, {self.apellido2}"