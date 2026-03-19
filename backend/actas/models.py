from django.db import models
from comunidad_info.models import *
from usuarios.models import *
import datetime

# Create your models here.

class Acta(models.Model):
    TIPO_OPTIONS=(
        ('ordinaria', 'ordinaria'),
        ('extraordinaria', 'extraordinaria')
    )

    CONV_OPTIONS=(
        ('primera', 'primera'),
        ('segunda', 'segunda')
    )

    titulo=models.CharField(max_length=200)
    fecha=models.DateField()
    tipo=models.CharField(max_length=15, choices=TIPO_OPTIONS, default='ordinaria')
    convocatoria=models.CharField(max_length=15, choices=CONV_OPTIONS, default='primera')
    lugar=models.CharField(max_length=200)
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='actas')
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='actas_creadas')
    usuarios=models.ManyToManyField(Usuario, related_name='actas', through='Asistencia')
    resuelta=models.BooleanField(default=False)

    class Meta:
        ordering=['-fecha']

    def __str__(self):
        return f"{self.fecha}, {self.tipo}, {self.convocatoria}, {'Resuelta' if self.resuelta else 'Pendiente'}"
    

class Asistencia(models.Model):
    acta=models.ForeignKey(Acta, on_delete=models.CASCADE, related_name='asistencia')
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asistencia')
    presente=models.BooleanField(default=False)
    representante=models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.acta.titulo}, {self.usuario.nombre}, {'Presente' if self.presente else 'Ausente'}"
    

class OrdenDia(models.Model):
    acta=models.ForeignKey(Acta, on_delete=models.CASCADE, related_name='puntos')
    descripcion=models.TextField(max_length=1000)

    class Meta:
        ordering=['-id']

    def __str__(self):
        return self.descripcion
    