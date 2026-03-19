from django.shortcuts import render
from rest_framework import generics, status, views
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
    try:
        # Verificamos si existe el perfil 'usuario'
        perfil = getattr(request.user, 'usuario', None)
        
        if not perfil:
            return Response({'error': 'El usuario no tiene un perfil asociado'}, status=404)

        return Response({
            'user_id': str(perfil.id),
            'username': request.user.username,
            'rol': perfil.rol
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# Crud usuarios
class UsuarioListCreate(generics.ListCreateAPIView):
    queryset=Usuario.objects.all()
    serializer_class=UsuarioSerializer

    def perform_create(self, serializer):

        user=User.objects.create_user(
            username=serializer.validated_data.pop('username'),
            password=serializer.validated_data.pop('password'),
        )

        return serializer.save(user=user)

class UsuarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Usuario.objects.all()
    serializer_class=UsuarioSerializer


# Crud comunidad
class ComunidadListCreate(generics.ListCreateAPIView):    
    serializer_class=ComunidadSerializer

    def get_queryset(self):
        queryset=Comunidad.objects.all()
        usuario_id=self.request.query_params.get('user')
        
        if usuario_id:
            usuario=Usuario.objects.get(pk=usuario_id)
            if usuario.rol == 'gestor':
                queryset=queryset.filter(gestor=usuario.id)

            else:
                queryset=queryset.filter(propiedades__usuario=usuario.id)

        return queryset

class ComunidadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comunidad.objects.all()
    serializer_class=ComunidadSerializer


# Crud propiedad
class PropiedadListCreate(generics.ListCreateAPIView):
    queryset=Propiedad.objects.all()
    serializer_class=PropeidadSerializer

class PropiedadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Propiedad.objects.all()
    serializer_class=PropeidadSerializer


# Crud comunicado
class ComunicadoListCreate(generics.ListCreateAPIView):
    queryset=Comunicado.objects.all()
    serializer_class=ComunicadoSerializer

class ComunicadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Comunicado.objects.all()
    serializer_class=ComunicadoSerializer


# Crud informacion
class InformacionListCreate(generics.ListCreateAPIView):
    queryset=Informacion.objects.all()
    serializer_class=InformacionSerializer

class InformacionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Informacion.objects.all()
    serializer_class=InformacionSerializer


# Crud incidencia
class IncidenciaListCreate(generics.ListCreateAPIView):
    queryset=Incidencia.objects.all()
    serializer_class=IncidenciaSerializer

class IncidenciaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Incidencia.objects.all()
    serializer_class=IncidenciaSerializer


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