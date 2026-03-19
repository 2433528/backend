from django.db import models
from usuarios.models import *
from comunidad_info.models import *

# Create your models here.

class Informacion(models.Model):
    titulo=models.CharField(max_length=200)
    texto=models.TextField(max_length=1000)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='info_creador')
    usuarios=models.ManyToManyField(Usuario, related_name='informaciones')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='informaciones', null=True)

    class Meta:
        ordering=['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo}, {self.usuario_creador.nombre}"