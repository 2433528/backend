from rest_framework import serializers
from usuarios.models import *
from comunidad_info.models import *
from comunicados.models import *
from info.models import *
from incidencias.models import *
from actas.models import *
from votos.models import *

class UsuarioSerializer(serializers.ModelSerializer):
    username=serializers.CharField(write_only=True)
    password=serializers.CharField(write_only=True)

    class Meta:
        model=Usuario
        exclude=['user','moroso']


class ComunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comunidad
        fields='__all__'


class PropeidadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Propiedad
        fields='__all__'


class ComunicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comunicado
        fields='__all__'


class InformacionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Informacion
        fields='__all__'


class IncidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Incidencia
        fields='__all__'


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