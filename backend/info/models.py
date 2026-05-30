from django.db import models
from usuarios.models import *
from comunidad_info.models import *

# Create your models here.

class Informacion(models.Model):
    titulo=models.CharField(max_length=200)
    texto=models.TextField(max_length=1000)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='info_creador')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='informaciones', null=True)

    class Meta:
        ordering=['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo}"
    

class Aviso(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    id_elemento=models.PositiveSmallIntegerField(null=True, blank=True)

    OPCIONES=[
        ('incidencia', 'incidencia'),
        ('convocatoria', 'convocatoria'),
        ('info', 'info'),
        ('acta', 'acta'),
        ('general', 'general'),
    ]

    tipo = models.CharField(max_length=50, choices=OPCIONES, default='general')

    def __str__(self):
        return f"{self.comunidad.nombre} {self.tipo}"
    



class AvisoUsuario(models.Model):
    aviso = models.ForeignKey(
        Aviso,
        on_delete=models.CASCADE,
        related_name='avisos_usuario'
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='avisos_usuario'
    )

    visto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.nombre} {self.aviso.tipo}"