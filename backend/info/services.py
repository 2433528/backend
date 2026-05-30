from django.db import transaction

from .models import Aviso, AvisoUsuario


def crear_aviso(instance, tipo):

    comunidad = instance.comunidad

    with transaction.atomic():

        aviso = Aviso.objects.create(
            comunidad=comunidad,
            tipo=tipo,
            id_elemento=instance.id
        )

        usuarios = comunidad.usuarios.all()

        AvisoUsuario.objects.bulk_create([
            AvisoUsuario(
                aviso=aviso,
                usuario=usuario
            )
            for usuario in usuarios
        ])

    return aviso