from django.shortcuts import render
from rest_framework import generics, status, views, exceptions
from rest_framework.response import Response
from usuarios.models import *
from comunidad_info.models import *
from comunicados.models import *
from info.models import *
from incidencias.models import *
from actas.models import *
from votos.models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .pagination import *
from django.contrib.auth.hashers import make_password

# Create your views here.

# Obtener el token
class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response=super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Quitamos el refresh del json para protegerlo
            refresh_token=response.data.pop('refresh')

            # Creamos la cookie en la que irá protegido el token de refresco
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                path='/api/refresh/',
                max_age=3600 * 24 * 7 # 7 días de duración
            )

        return response

            
# Refrescar el token
class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Obtenemos el token de refresco de la cookie
        refresh_token=request.COOKIES.get('refresh_token')

        # Lo metemos en el body manualmente
        if refresh_token:
            data = request.data.copy()
            data['refresh']=refresh_token
            serializer = self.get_serializer(data=data)

            try:
                serializer.is_valid(raise_exception=True)

            except Exception as e:
                return Response({'detail': str(e)}, status=401)
                    
            return Response(serializer.validated_data, status=200)

        return Response({'detail': 'Refresh token no encontrado.'}, status=401)


# Cerrar la sesión
class LogoutView(views.APIView):
    def post(self, request):
        response=Response({
            'message':'Sesión cerrada'
        }, status=status.HTTP_200_OK)

        # Borramos la cookie del navegador
        response.delete_cookie('refresh_token', path='/api/refresh/')

        return response


# Clave vapid notificaciones
@api_view(['GET'])
def vapid_key(request):
    return Response({
        'public_key': settings.WEBPUSH_SETTINGS.get('VAPID_PUBLIC_KEY')
    })

# Obtener el usuario
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    return Response({
        'user_id': str(request.user.usuario.id) or '',
        'username':request.user.username,
        'nombre':request.user.usuario.nombre
    })


# Crud usuarios
class UsuarioListCreate(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]   
    serializer_class=UsuarioSerializer
    pagination_class=MiPaginacion

    def get_queryset(self):
        queryset=Usuario.objects.all()
        comunidad=self.request.query_params.get('comunidad')
        dni=self.request.query_params.get('dni')

        if dni:
            queryset=queryset.filter(dni=dni)
            return queryset

        if comunidad:
            queryset=queryset.filter(propiedades__comunidad__id=comunidad)
            return queryset
        
        return Usuario.objects.none()

class UsuarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Usuario.objects.all()
    serializer_class=UsuarioSerializer

    def perform_update(self, serializer):
        usuario=self.get_object()
        password=self.request.data.get('password')
        comunidad_id=serializer.validated_data.get('comunidad')
        nuevo_rol=serializer.validated_data.get('rol')
        nuevo_moroso=serializer.validated_data.get('moroso')

        if comunidad_id:
            item=RolComunidad.objects.filter(usuario=usuario, comunidad_id=comunidad_id).exclude(rol='gestor').first()
        
        if item:            
            item.rol=nuevo_rol
            item.moroso=nuevo_moroso
            item.save()

        if not password:       
            return serializer.save(password=usuario.user.password)
        
        hash_password=make_password(password)
        usuario.user.password=hash_password
        usuario.user.save()
        serializer.save(password=hash_password)

# Crud comunidad
class ComunidadListCreate(generics.ListCreateAPIView):    
    queryset=Comunidad.objects.all()
    serializer_class=ComunidadSerializer

class ComunidadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comunidad.objects.all()
    serializer_class=ComunidadSerializer


# Crud propiedad
class PropiedadListCreate(generics.ListCreateAPIView):    
    serializer_class=PropeidadSerializer
    pagination_class=MiPaginacion

    def get_queryset(self):
        queryset=Propiedad.objects.all()
        comunidad=self.request.query_params.get('comunidad')
        num_letra=self.request.query_params.get('num_piso')

        if comunidad and num_letra:
            queryset=queryset.filter(comunidad__id=comunidad, num_letra=num_letra)
            return queryset
        
        if comunidad:
            queryset=queryset.filter(comunidad__id=comunidad)
            return queryset

        return Propiedad.objects.none()
        
    def perform_create(self, serializer):
        propietario=serializer.validated_data.pop('usuario_dni')
        comunidad=serializer.validated_data.get('comunidad')
    
        if propietario and comunidad:
            propietario=Usuario.objects.filter(dni=propietario).first()
            return serializer.save(comunidad=comunidad, usuario=propietario)

        raise ValidationError('Datos no válidos.')

class PropiedadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Propiedad.objects.all()
    serializer_class=PropeidadSerializer


# Crud RolComunidad
class RolComunidadListCreate(generics.ListCreateAPIView):    
    serializer_class=RolComunidadSerializer

    def get_queryset(self):
        queryset=RolComunidad.objects.all()
        usuario_id=self.request.query_params.get('user')
        comunidad=self.request.query_params.get('comunidad')

        if usuario_id:
            queryset=queryset.filter(usuario__id=usuario_id)
            print(queryset)
            return queryset
        
        if comunidad:
            queryset=queryset.filter(comunidad__id=comunidad)
            return queryset

        return RolComunidad.objects.none()
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except:
            raise ValidationError({
                "rol": "Este usuario ya tiene un rol incompatible en esta comunidad."
            })

class RolComunidadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=RolComunidad.objects.all()
    serializer_class=RolComunidadSerializer


# Crud comunicado
class ComunicadoListCreate(generics.ListCreateAPIView):
    queryset=Comunicado.objects.all()
    serializer_class=ComunicadoSerializer

class ComunicadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comunicado.objects.all()
    serializer_class=ComunicadoSerializer


# Crud informacion
class InformacionListCreate(generics.ListCreateAPIView):
    serializer_class=InformacionSerializer

    def get_queryset(self):
        queryset=Informacion.objects.all()
        comunidad=self.request.query_params.get('comunidad')

        if comunidad:
            comunidad=Comunidad.objects.get(pk=comunidad)
            queryset=queryset.filter(comunidad=comunidad)

        return queryset

class InformacionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Informacion.objects.all()
    serializer_class=InformacionSerializer


# Crud incidencia
class IncidenciaListCreate(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]    
    serializer_class=IncidenciaSerializer
    pagination_class=MiPaginacion

    def get_queryset(self):
        queryset=Incidencia.objects.all();
        comunidad=self.request.query_params.get('comunidad')
        roles=self.request.user.usuario.roles.all().values_list('rol', flat=True)

        if comunidad:
            comunidad=Comunidad.objects.get(pk=comunidad)
            queryset=queryset.filter(comunidad=comunidad)

        if not 'gestor' in roles:
            queryset=queryset.filter(usuario_creador__user=self.request.user)

        return queryset

class IncidenciaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Incidencia.objects.all()
    serializer_class=IncidenciaSerializer

class CambiarStadoIncidencia(views.APIView):
    def patch(self, request, pk):
        try:
            incidencia = Incidencia.objects.get(pk=pk)
        except Incidencia.DoesNotExist:
            return Response(
                {'mensaje': 'No encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CambiarEstadoIncidenciaSerializer(
            incidencia,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Estado cambiado'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Crud actas
class ActaListCreate(generics.ListCreateAPIView):
    queryset=Acta.objects.all()
    serializer_class=ActaSerializer

class ActaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Acta.objects.all()
    serializer_class=ActaSerializer


# Crud asistencia
class AsistenciaListCreate(generics.ListCreateAPIView):
    queryset=Asistencia.objects.all()
    serializer_class=AsistenciaSerializer

class AsistenciaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Asistencia.objects.all()
    serializer_class=AsistenciaSerializer


# Orden dia
class OrdenDiaListCreate(generics.ListCreateAPIView):
    queryset=OrdenDia.objects.all()
    serializer_class=OrdenDiaSerializer

class OrdenDiaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=OrdenDia.objects.all()
    serializer_class=OrdenDiaSerializer


# Crud votacion
class VotacionListCreate(generics.ListCreateAPIView):
    queryset=Votacion.objects.all()
    serializer_class=VotacionSerializer

class VotacionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Votacion.objects.all()
    serializer_class=VotacionSerializer


# Crud voto
class VotoListCreate(generics.ListCreateAPIView):
    queryset=Voto.objects.all()
    serializer_class=VotoSerializer

class VotoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Voto.objects.all()
    serializer_class=VotoSerializer