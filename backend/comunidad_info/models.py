from django.db import models
from usuarios.models import *
from django.db.models import Q
from django.core.exceptions import ValidationError

# Create your models here.

class Comunidad(models.Model):
    nombre=models.CharField(max_length=200)
    calle=models.CharField(max_length=200)
    numero=models.PositiveSmallIntegerField(null=True, blank=True)
    cod_postal=models.CharField(max_length=5)
    localidad=models.CharField(max_length=200)
    provincia=models.CharField(max_length=200, null=True, blank=True)
    cif=models.CharField(max_length=9, help_text='Código de identificación fiscal', unique=True)
    usuarios=models.ManyToManyField(Usuario, related_name='comunidades', through='RolComunidad')

    def __str__(self):
        return f"{self.nombre}, {self.calle}, {self.numero}, {self.cod_postal}, {self.localidad}"
    

class Propiedad(models.Model):
    num_letra=models.CharField(max_length=5)
    usuario=models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='propiedades')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='propiedades')

    class Meta:
        constraints=[
            models.UniqueConstraint(
            fields=['num_letra', 'comunidad'],
            name='propiedad_unica_en_la_comunidad'
            )
        ]

    def save(self, *args, **kwargs):
        if self.num_letra:
            self.num_letra = self.num_letra.upper().strip()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.num_letra}, {self.comunidad.nombre}, {self.usuario.nombre if self.usuario else ''}"
    

class RolComunidad(models.Model):
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='roles')
    comunidad=models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='roles')

    ROL_OPTIONS=(
        ('gestor', 'gestor'),
        ('presidente', 'presidente'),
        ('propietario', 'propietario'),
        ('vicepresidente', 'vicepresidente'),
        ('secretario', 'secretario'),
    )

    rol=models.CharField(max_length=30, choices=ROL_OPTIONS, default='propietario')
    moroso=models.BooleanField(default=False)

    class Meta:
        ordering=['comunidad__nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['comunidad'],
                condition=Q(rol='gestor'),
                name='unico_gestor_por_comunidad'
            ),
            models.UniqueConstraint(
                fields=['comunidad'],
                condition=Q(rol='presidente'),
                name='unico_presidente_por_comunidad'
            ),
            models.UniqueConstraint(
                fields=['comunidad'],
                condition=Q(rol='vicepresidente'),
                name='unico_vicepresidente_por_comunidad'
            ),
            models.UniqueConstraint(
                fields=['comunidad'],
                condition=Q(rol='secretario'),
                name='unico_secretario_por_comunidad'
            ),
            models.UniqueConstraint(
            fields=['usuario', 'comunidad'],
            condition=Q(rol__in=['presidente', 'vicepresidente', 'secretario', 'propietario']),
            name='un_solo_rol_por_usuario_comunidad'
            )
        ]

    def __str__(self):
        return f"{self.rol}, {self.usuario.nombre}, {self.comunidad.nombre}"
    