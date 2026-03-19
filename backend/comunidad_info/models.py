from django.db import models
from usuarios.models import *

# Create your models here.

class Comunidad(models.Model):
    nombre=models.CharField(max_length=200)
    calle=models.CharField(max_length=200)
    numero=models.PositiveSmallIntegerField(null=True, blank=True)
    cod_postal=models.CharField(max_length=5)
    localidad=models.CharField(max_length=200)
    provincia=models.CharField(max_length=200, null=True, blank=True)
    cif=models.CharField(max_length=9, help_text='Código de identificación fiscal', unique=True)
    gestor=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comunidad', null=True)

    def __str__(self):
        return f"{self.nombre}, {self.calle}, {self.numero}, {self.cod_postal}, {self.localidad}"
    

class Propiedad(models.Model):
    num_letra=models.CharField(max_length=5)
    usuario=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='propiedades')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='propiedades')