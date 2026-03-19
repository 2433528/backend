# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from webpush import send_user_notification
# from .models import Comunicado

# @receiver(post_save, sender=Comunicado)
# def notificar_nuevo_comunicado(sender, instance, created, **kwargs):
#     if created:
#         # Preparamos el mensaje
#         payload = {
#             "head": "Nuevo Comunicado ",
#             "body": instance.titulo,
#             "url": "/comunicados/"
#         }
        
#         # Enviamos a todos los usuarios de la comunidad
#         usuarios = instance.comunidad.usuarios.all()
        
#         for usuario in usuarios:
#             # Envia a cada usuario suscrito
#             send_user_notification(user=usuario, payload=payload, ttl=1000)



from django.db.models.signals import post_save
from django.dispatch import receiver
from webpush import send_user_notification
from .models import Comunicado

@receiver(post_save, sender=Comunicado)
def notificar_nuevo_comunicado(sender, instance, created, **kwargs):
    print('señal activada')
    if created and instance.usuario_creador:
        from django.contrib.auth.models import User
        yo = User.objects.get(username='cris')
        
                
        payload = {
            "head": "Nuevo Comunicado 📢",
            "body": 'Esto es un aviso',
            "url": f"/"
        }
        
        
        send_user_notification(user=yo, payload=payload, ttl=1000)
