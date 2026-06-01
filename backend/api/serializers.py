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
        exclude=['usuarios']

    
    def save(self, **kwargs):
        nueva = self.instance is None
        comunidad=super().save(**kwargs)

        if nueva:
            RolComunidad.objects.create(
                usuario=self.context.get('request').user.usuario,
                comunidad=comunidad,
                rol='gestor'
            )   

        return comunidad

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
    propiedades=serializers.SerializerMethodField()
    class Meta:
        model=Usuario
        fields=['id', 'nombre', 'apellido1', 'apellido2', 'dni', 'propiedades']

    def get_propiedades(self, obj):
        comunidad = self.context['request'].query_params.get('comunidad')
        return [
            p.num_letra
            for p in obj.propiedades.all().filter(comunidad_id=comunidad)
        ]


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
        datos=[]
        relaciones=ComunicadoUsuario.objects.filter(comunicado=comunicado).distinct().values('usuario__nombre', 'usuario__apellido1', 'usuario__apellido2', 'usuario__dni', 'leido')
        for rel in relaciones:
            datos.append({
                'nombre':f'{rel['usuario__nombre']} {rel['usuario__apellido1']} {rel['usuario__apellido2']}', 
                'dni':rel['usuario__dni'], 
                'leido':rel['leido'],
                'propiedades':', '.join(list(Propiedad.objects.filter(usuario__dni=rel['usuario__dni']).values_list('num_letra', flat=True).distinct()))
            })
        
        return datos

    def get_leido(self, comunicado):
        valor=ComunicadoUsuario.objects.filter(comunicado=comunicado, usuario=self.context['request'].user.usuario).values_list('leido', flat=True).distinct().first()
        return valor
    
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
    fecha_bonita = serializers.DateTimeField(source='fecha_creacion', format="%d-%m-%Y", read_only=True)
    class Meta:
        model=Informacion
        fields='__all__'


class IncidenciaSerializer(serializers.ModelSerializer):
    fecha_bonita = serializers.DateTimeField(source='fecha_creacion', format="%d-%m-%Y", read_only=True)
    usuario_creador = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=Incidencia
        fields='__all__'

    def get_usuario_creador(self, incidencia):        
        if incidencia:
            comunidad=self.context['request'].query_params.get('comunidad')
            propiedades=Propiedad.objects.filter(usuario=incidencia.usuario_creador, comunidad__id=comunidad).values_list('num_letra', flat=True).distinct()
            return {'nombre':f"""
                    {incidencia.usuario_creador.nombre} 
                    {incidencia.usuario_creador.apellido1} 
                    {incidencia.usuario_creador.apellido2 if incidencia.usuario_creador.apellido2 else ''}""", 
                    'dni':incidencia.usuario_creador.dni,
                    'propiedades':', '.join(propiedades)
                    }

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
    usuarios=UsuarioSerializer(many=True, read_only=True)  

    class Meta:
        model=Acta
        fields='__all__'



class AsistenciaSerializer(serializers.ModelSerializer):
    asistentes=serializers.ListField(write_only=True)
    usuario=UsuarioSerializer(read_only=True)
    
    class Meta:
        model=Asistencia
        exclude=['acta']


import csv
import io
from rest_framework import serializers
from django.db import transaction


class ComunidadFicheroSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def validate_archivo(self, value):
        if value.size > (3 * 1024 * 1024):
            raise serializers.ValidationError("El archivo supera el límite permitido de 3 MB.")
        
        nombre_archivo = value.name
        if not nombre_archivo.endswith('.csv'):
            raise serializers.ValidationError("El archivo debe tener la extensión .csv")
        
        tipos_validos = ['text/csv', 'application/csv', 'application/vnd.ms-excel', 'text/plain']
        if value.content_type not in tipos_validos:
            raise serializers.ValidationError("El formato del archivo no es un CSV válido.")
            
        return value
    
    def save(self):
        archivo = self.validated_data['archivo']
        
        archivo_texto = io.StringIO(archivo.read().decode('utf-8-sig'))
        lector_csv = csv.DictReader(archivo_texto)
       
        with transaction.atomic():
            for fila in lector_csv:
                # Evita duplicados
                if Comunidad.objects.filter(cif=fila['cif']).exists():
                    raise serializers.ValidationError(
                        f"Error en el CSV: La comunidad con CIF {fila['cif']} ya está registrada."
                    )

                comunidad=Comunidad.objects.create(
                    nombre=fila['nombre'],
                    calle=fila['calle'],
                    numero=int(fila['numero']) if fila.get('numero') else None,
                    cod_postal=fila['cod_postal'],
                    localidad=fila['localidad'],
                    provincia=fila.get('provincia', ''),
                    cif=fila['cif'],
                )
    
                RolComunidad.objects.create(
                    usuario=self.context.get('request').user.usuario,
                    comunidad=comunidad,
                    rol='gestor'
                )             
                
        return 


class PropietariosFicheroSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def validate_archivo(self, value):
        if value.size > (3 * 1024 * 1024):
            raise serializers.ValidationError("El archivo supera el límite permitido de 3 MB.")
        
        nombre_archivo = value.name
        if not nombre_archivo.endswith('.csv'):
            raise serializers.ValidationError("El archivo debe tener la extensión .csv")
        
        tipos_validos = ['text/csv', 'application/csv', 'application/vnd.ms-excel', 'text/plain']
        if value.content_type not in tipos_validos:
            raise serializers.ValidationError("El formato del archivo no es un CSV válido.")
            
        return value
    

    def save(self):
        archivo = self.validated_data['archivo']
        
        archivo_texto = io.StringIO(archivo.read().decode('utf-8-sig'))
        lector_csv = csv.DictReader(archivo_texto)
        

        with transaction.atomic():
            for fila in lector_csv:
                try:
                    comunidad = Comunidad.objects.get(cif=fila['cif_comunidad'])
                except:
                    raise serializers.ValidationError(
                        f"La comunidad con ID {fila.get('comunidad_id')} no existe o falta en el CSV."
                    )

                user,created=User.objects.get_or_create(
                    username=fila['dni'],
                )

                if created:
                    user.set_password('Comunidad12345')
                    user.save()

                # Crear o recuperar el usuario, sirve para evitar repeticiones. Creado almacena true o false.
                usuario, created = Usuario.objects.update_or_create(
                    user=user,
                    defaults={
                        'dni': fila['dni'],
                        'nombre': fila['nombre'],
                        'apellido1': fila['apellido1'],
                        'apellido2': fila.get('apellido2', ''),
                        'telefono': fila.get('telefono', ''),
                        'email': fila['email'],
                    }
                )
                
                # Crear la propiedad asociada
                num_letra = fila['num_letra'].upper().strip()
                propiedad,created=Propiedad.objects.get_or_create(
                    num_letra=num_letra,
                    comunidad=comunidad,
                    # Al poner el usuario aquí no salta la regla de único
                    defaults={
                        "usuario": usuario
                    }
                )

                if not created:
                    propiedad.usuario = usuario
                    propiedad.save()
                
                if not RolComunidad.objects.filter(usuario=usuario, comunidad=comunidad, rol='gestor').exists():
                    RolComunidad.objects.get_or_create(
                        usuario=usuario,
                        comunidad=comunidad,
                        defaults={'rol': 'propietario'}
                    )
                else:
                    RolComunidad.objects.create(
                        usuario=usuario,
                        comunidad=comunidad,
                        rol='propietario'
                    )
                
        return
    
class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Aviso
        fields='__all__'
        
        
    