from django.db.models.signals import post_save
from django.dispatch import receiver
from info.models import *
from incidencias.models import *
from actas.models import *
from .services import crear_aviso

@receiver(post_save, sender=Convocatoria)
def convocatoria_signal(sender, instance, created, **kwargs):

    if created:
        crear_aviso(instance, 'convocatoria')


@receiver(post_save, sender=Incidencia)
def incidencia_signal(sender, instance, created, **kwargs):

    if created:
        crear_aviso(instance, 'incidencia')


@receiver(post_save, sender=Acta)
def acta_signal(sender, instance, created, **kwargs):

    if created:
        crear_aviso(instance, 'acta')


@receiver(post_save, sender=Informacion)
def informacion_signal(sender, instance, created, **kwargs):

    if created:
        crear_aviso(instance, 'info')