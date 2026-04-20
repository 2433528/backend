from django.db import models
from comunidad_info.models import *
from usuarios.models import *
import datetime

# Create your models here.
class Convocatoria(models.Model):
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
    hora=models.TimeField(null=True)
    tipo=models.CharField(max_length=15, choices=TIPO_OPTIONS, default='ordinaria')
    lugar=models.CharField(max_length=200)
    num_convocatoria=models.CharField(max_length=15, choices=CONV_OPTIONS, default='primera')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='convocatorias')
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='convocatorias_creadas')
    celebrada=models.BooleanField(default=False)

    class Meta:
        ordering=['-fecha']

    def __str__(self):
        return f"{self.titulo}, {self.fecha}, {self.tipo}"

class Acta(models.Model):
    convocatoria=models.OneToOneField(Convocatoria, on_delete=models.CASCADE, related_name='acta_convocatoria')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='actas')
    usuario_creador=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='actas_creadas')
    usuarios=models.ManyToManyField(Usuario, related_name='actas', through='Asistencia')
    resuelta=models.BooleanField(default=False)
    timestamp_inicio=models.DateTimeField(auto_now_add=True, null=True)  
    timestamp_fin=models.DateTimeField(null=True, blank=True)
    resumen=models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return f"{self.convocatoria.titulo}, {'Resuelta' if self.resuelta else 'Pendiente'}"
    

class Asistencia(models.Model):
    acta=models.ForeignKey(Acta, on_delete=models.CASCADE, related_name='asistencia')
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asistencia')
    presente=models.BooleanField(default=False)
    representante=models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together=[('acta', 'usuario'),]

    def __str__(self):
        return f"{self.acta.convocatoria.titulo}, {self.usuario.nombre}, {'Presente' if self.presente else 'Ausente'}"
    

class OrdenDia(models.Model):
    convocatoria=models.ForeignKey(Convocatoria, on_delete=models.CASCADE, related_name='puntos')
    acta=models.ForeignKey(Acta, on_delete=models.SET_NULL, related_name='puntos', null=True, blank=True)
    descripcion=models.TextField(max_length=1000)

    class Meta:
        ordering=['-id']

    def __str__(self):
        return self.descripcion
    