from django.contrib import admin
from .models import *
from webpush.models import *

# Register your models here.
admin.site.register(Comunicado)
admin.site.register(ComunicadoUsuario)
admin.site.register(SubscriptionInfo)
