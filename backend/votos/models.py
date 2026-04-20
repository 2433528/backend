from django.db import models
from actas.models import *

# Create your models here.

class Votacion(models.Model):
    punto=models.OneToOneField(OrdenDia, on_delete=models.CASCADE, related_name='votacion')
    voto_favor=models.PositiveIntegerField(default=0)
    voto_contra=models.PositiveIntegerField(default=0)
    abstencion=models.PositiveIntegerField(default=0)
    favorable=models.BooleanField(default=False)
    abierta=models.BooleanField(default=False)
    apertura=models.DateTimeField(auto_now_add=True)
    cierre=models.DateTimeField(null=True, blank=True)

    #Calcula si el resultado es favorable.
    def actualizar_resultado(self):        
        if self.voto_favor > self.voto_contra:
            self.favorable = True
        else:
            self.favorable = False
        self.save()
        
    
    def __str__(self):
        return f"{self.punto.descripcion}, {self.favorable}"
    


class Voto(models.Model):
    OPTIONS=(
        ('Favor', 'Favor'),
        ('Contra', 'Contra'),
        ('Abstencion', 'Abstencion')
    )

    opcion=models.CharField(max_length=10, choices=OPTIONS, default='Favor')
    votacion=models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name='voto')
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='voto')
    fecha=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('votacion', 'usuario')

    def __str__(self):
        return self.opcion