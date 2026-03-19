from django.db.models.signals import post_save # Señal de guardado reciente
from django.dispatch import receiver
from .models import Voto, Votacion

# @receiver capta la señal y recibe una instancia
@receiver(post_save, sender=Voto)
def recalcular_totales(sender, instance, created, **kwargs):
    if created:
        # Mira a que votacion pertenece
        votacion = instance.votacion
        
        # Contamos cada tipo de voto
        votacion.voto_favor = Voto.objects.filter(votacion=votacion, opcion='Favor').count()
        votacion.voto_contra = Voto.objects.filter(votacion=votacion, opcion='Contra').count()
        votacion.abstencion = Voto.objects.filter(votacion=votacion, opcion='Abstencion').count()
        
        # Aprovechamos para actualizar si es favorable o no
        if votacion.voto_favor > votacion.voto_contra:
            votacion.favorable = True
        else:
            votacion.favorable = False
            
        votacion.save()