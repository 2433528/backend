from django.db import models
from usuarios.models import Usuario
from comunidad_info.models import *

# Create your models here.

class Comunicado(models.Model):
    titulo=models.CharField(max_length=200)
    texto=models.TextField(max_length=1000)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='creador_comunicado')
    usuarios=models.ManyToManyField(Usuario, related_name='comunicados', through='ComunicadoUsuario')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='comunicados', null=True)

    class Meta:
        ordering=['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo}, {self.usuario_creador.nombre}"


class ComunicadoUsuario(models.Model):
    comunicado=models.ForeignKey(Comunicado, on_delete=models.CASCADE, related_name='comunicado_usuario')
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comunicado_usuario')
    leido=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.comunicado.titulo}, {'Leido' if self.leido else 'No leido'}"
