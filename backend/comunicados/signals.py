from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comunicado
from webpush.utils import send_notification_to_user
import json

@receiver(post_save, sender=Comunicado, dispatch_uid="notificar_comunicado_unico")
def notificar_nuevo_comunicado(sender, instance, created, **kwargs): 
    if created:
        # 1. Qué dirá la notificación
        payload = {
            "head": "Nuevo Comunicado 📢",
            "body": str(instance.comunidad.nombre or ""),
            "url": "https://frontend-x64j.onrender.com" # Poner URL front
        }

        # 2. Obtenemos los usuarios que deben recibirla
        usuarios = instance.comunidad.usuarios.all().distinct()
       
        for usuario in usuarios:
            send_notification_to_user(user=usuario.user, payload=json.dumps(payload), ttl=1000)
