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
    propiedad=serializers.SerializerMethodField()
     
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
    
    def get_propiedad(self, usuario):
        comunidad_id = self.context.get('request').query_params.get('comunidad')
        
        if not comunidad_id:
            return ""

        propiedades = Propiedad.objects.filter(
            comunidad_id=comunidad_id, 
            usuario_id=usuario.id
        ).values_list('num_letra', flat=True)
    
        return ", ".join(propiedades)

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


class ComunicadoDestinatarioSerializer(serializers.ModelSerializer):
    class Meta:
        model=Usuario
        fields=['id', 'nombre', 'apellido1', 'apellido2', 'dni']


class ComunicadoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model=ComunicadoUsuario
        fields='__all__'
        read_only_fields = ('comunicado', 'usuario')


class ComunicadoSerializer(serializers.ModelSerializer):
    fecha_creacion=serializers.DateTimeField(format="%d-%m-%Y", read_only=True)    
    usuarios = serializers.SerializerMethodField(read_only=True)
    destinatarios=serializers.ListField(write_only=True)
    comunicadousuario=serializers.SerializerMethodField(read_only=True)
    leido=serializers.SerializerMethodField()
    
    class Meta:
        model=Comunicado
        fields='__all__'

    def get_usuarios(self, comunicado):
        relaciones =ComunicadoUsuario.objects.filter(comunicado=comunicado).distinct().values('usuario__nombre', 'usuario__apellido1', 'usuario__apellido2', 'usuario__dni', 'leido')

        return [{'nombre':f'{rel['usuario__nombre']} {rel['usuario__apellido1']} {rel['usuario__apellido2']}', 'dni':rel['usuario__dni'], 'leido':rel['leido']} for rel in relaciones]


    def get_leido(self, comunicado):
        valor=ComunicadoUsuario.objects.filter(comunicado=comunicado, usuario=self.context['request'].user.usuario).values_list('leido', flat=True).first()
        return valor if valor is not None else False
    
    def get_comunicadousuario(self, comunicado):
        comunicadousu=ComunicadoUsuario.objects.filter(comunicado=comunicado, usuario=self.context['request'].user.usuario).first()
        return comunicadousu.id if comunicadousu else None


    def create(self, validated_data):
        destinatarios_data = validated_data.pop('destinatarios', [])
        
        comunicado = Comunicado.objects.create(
            titulo=validated_data.get('titulo'),
            texto=validated_data.get('texto'),
            usuario_creador=self.context['request'].user.usuario,
            comunidad=validated_data.get('comunidad'),
        )
        
        for destinatario in destinatarios_data:
            ComunicadoUsuario.objects.create(
                comunicado=comunicado,
                usuario=Usuario.objects.get(pk=destinatario['id'])
            )

        return comunicado
    

class InformacionSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    class Meta:
        model=Informacion
        fields='__all__'


class IncidenciaSerializer(serializers.ModelSerializer):
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    usuario_creador = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=Incidencia
        fields='__all__'

    def get_usuario_creador(self, incidencia):
        if incidencia:
            return {'nombre':f"{incidencia.usuario_creador.nombre} {incidencia.usuario_creador.apellido1} {incidencia.usuario_creador.apellido2 if incidencia.usuario_creador.apellido2 else ''}", 'dni':incidencia.usuario_creador.dni}
        return None
    
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
        


class VotacionSerializer(serializers.ModelSerializer):
    punto=serializers.PrimaryKeyRelatedField(read_only=True)
    voto=serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=Votacion
        fields='__all__'

    def get_voto(self, obj):
        return Voto.objects.filter(usuario=self.context['request'].user.usuario, votacion=obj).exists()

class VotoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Voto
        exclude=['usuario']



class OrdenDiaSerializer(serializers.ModelSerializer):
    votacion=VotacionSerializer(read_only=True)
    class Meta:
        model=OrdenDia
        fields='__all__'



class ConvocatoriaSerializer(serializers.ModelSerializer):
    puntos=serializers.ListField(write_only=True)
    hora = serializers.TimeField(format="%H:%M")
    fecha_lectura = serializers.DateField(source='fecha', format="%d-%m-%Y", read_only=True)
    fecha=serializers.DateField(input_formats=['%d-%m-%Y', '%Y-%m-%d'], format="%Y-%m-%d")
    lista_puntos=OrdenDiaSerializer(source='puntos', many=True, read_only=True)
    creador=UsuarioSerializer(source='usuario_creador', read_only=True)
    acta=serializers.SerializerMethodField()

    class Meta:
        model=Convocatoria
        fields='__all__'

    def validate(self, data):
        fecha = data.get('fecha')
        hora = data.get('hora')
        celebrada = data.get('celebrada', self.instance.celebrada if self.instance else False)

        if fecha and hora:
            dt = datetime.datetime.combine(fecha, hora)
            ahora = datetime.datetime.now()

            if not celebrada and dt < ahora:
                raise serializers.ValidationError({'datetime': 'La fecha o la hora no puede ser menor a la actual.'})

            if celebrada and ahora > (dt + datetime.timedelta(minutes=10)):
                raise serializers.ValidationError({'celebrada': 'El tiempo de cortesía (10 min) para cerrar esta convocatoria ha expirado.'})
        
        if self.instance and self.instance.celebrada:
            raise serializers.ValidationError({'error': 'Esta convocatoria ya fue celebrada y no admite más cambios.'})
    
        return data
    
    def get_acta(self, obj):
        try:
            acta=obj.acta_convocatoria
            return True
        except:
            return False
    
class ActaSerializer(serializers.ModelSerializer):
    pertenece_convocatoria=ConvocatoriaSerializer(source='convocatoria', read_only=True)    

    class Meta:
        model=Acta
        fields='__all__'

class AsistenciaSerializer(serializers.ModelSerializer):
    asistentes=serializers.ListField(write_only=True)
    
    class Meta:
        model=Asistencia
        fields=['asistentes']

