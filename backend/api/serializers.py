from rest_framework import serializers
from django.db.models import Case, When, Value, IntegerField
from usuarios.models import *
from comunidad_info.models import *
from comunicados.models import *
from info.models import *
from incidencias.models import *
from actas.models import *
from votos.models import *
from django.db import transaction

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=False,
        allow_blank=True,
    )

    comunidad = serializers.IntegerField(write_only=True, required=False)
    rol = serializers.CharField(write_only=True, required=False, default='propietario')
    moroso = serializers.BooleanField(write_only=True, required=False, default=False)
    moroso_info = serializers.SerializerMethodField()
    rol_info = serializers.SerializerMethodField()
     
    class Meta:
        model=Usuario
        exclude=['user']

    def __init__(self, *args, **kwargs):
        super(UsuarioSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['password'].required = False
            self.fields['password'].allow_blank = True
        else:
            self.fields['password'].required = True
            self.fields['password'].allow_blank = False


    def create(self, validated_data):
        password = validated_data.pop('password')
        comunidad = validated_data.pop('comunidad', None)
        rol = validated_data.pop('rol', 'propietario')
        dni = validated_data.get('dni')
        moroso = validated_data.pop('moroso')

        with transaction.atomic():
            user = User.objects.create_user(
                username=dni, 
                password=password
            )

            usuario_perfil = Usuario.objects.create(user=user, **validated_data)
            
            if comunidad:
                comunidad=Comunidad.objects.get(pk=comunidad)
                RolComunidad.objects.create(
                    usuario=usuario_perfil,
                    comunidad=comunidad,
                    rol=rol,
                    moroso=moroso
                )

            return usuario_perfil
        
    def _get_mejor_rol(self, usuario):
        comunidad_id = self.context.get('request').query_params.get('comunidad')
        
        return usuario.roles.filter(comunidad_id=comunidad_id).annotate(
            prioridad=Case(
                When(rol='gestor', then=Value(1)),
                When(rol='presidente', then=Value(2)),
                When(rol='vicepresidente', then=Value(3)),
                When(rol='secretario', then=Value(4)),
                When(rol='propietario', then=Value(5)),
                default=Value(6),
                output_field=IntegerField(),
            )
        ).order_by('prioridad').first()

    def get_rol_info(self, usuario):
        rol_obj = self._get_mejor_rol(usuario)
        return rol_obj.rol if rol_obj else None

    def get_moroso_info(self, usuario):
        comunidad_id = self.context.get('request').query_params.get('comunidad')
        
        if not comunidad_id:
            return False
        
        return usuario.roles.filter(comunidad_id=comunidad_id, moroso=True).exists()



class ComunidadSerializer(serializers.ModelSerializer):    

    class Meta:
        model=Comunidad
        fields='__all__'


class PropeidadSerializer(serializers.ModelSerializer):
    usuario_dni = serializers.CharField(write_only=True)
    nombre_usu=serializers.CharField(source='usuario.nombre', read_only=True)
    apellido1_usu=serializers.CharField(source='usuario.apellido1', read_only=True)
    apellido2_usu=serializers.CharField(source='usuario.apellido2', read_only=True)
    dni_usu=serializers.CharField(source='usuario.dni', read_only=True)

    class Meta:
        model=Propiedad
        fields='__all__'


class RolComunidadSerializer(serializers.ModelSerializer):
    com_name=serializers.CharField(source='comunidad.nombre', read_only=True)
    com_localidad=serializers.CharField(source='comunidad.localidad', read_only=True)
    usu_nombre=serializers.CharField(source='usuario.nombre', read_only=True)
    class Meta:
        model = RolComunidad
        fields = '__all__'

    def validate(self, data):
        
        # Valida que en una comunidad solo haya un presidente, vicepresidente y secretario.        
        rol = data.get('rol')
        comunidad = data.get('comunidad')
        instance = getattr(self, 'instance', None)

        if rol in ['presidente', 'vicepresidente', 'secretario']:
            qs = RolComunidad.objects.filter(rol=rol, comunidad=comunidad)
            
            if instance:
                qs = qs.exclude(pk=instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError(
                    f"Ya existe un {rol} en la comunidad {comunidad.nombre}."
                )

        return data
    

class MorosoSerializer(serializers.ModelSerializer):
    class Meta:
        model=RolComunidad
        field=['moroso']


class ComunicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comunicado
        fields='__all__'


class InformacionSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    class Meta:
        model=Informacion
        fields='__all__'


class IncidenciaSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    class Meta:
        model=Incidencia
        fields='__all__'

class CambiarEstadoIncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Incidencia
        fields=['estado']


    def validate_estado(self, value):
        instance = self.instance

        if instance:
            if instance.estado == 'inicio' and value != 'proceso':
                raise serializers.ValidationError('Despues de inicio se debe pasar a proceso')
            
            if instance.estado == 'proceso' and value != 'resuelta':
                raise serializers.ValidationError('Despues de proceso se debe pasar a resuelta')

        return value
        

class ActaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Acta
        fields='__all__'


class OrdenDiaSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrdenDia
        fields='__all__'


class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Asistencia
        fields='__all__'


class VotacionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Votacion
        fields='__all__'


class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Voto
        fields='__all__'