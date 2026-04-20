from django.urls import path
from .views import *

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view()),
    path('refresh/', MyTokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('getuser/', get_user),

    # Crud usuarios
    path('usuarios/', UsuarioListCreate.as_view()),
    path('usuarios/<int:pk>/', UsuarioDetail.as_view()),

    # Crud comunidades
    path('comunidades/', ComunidadListCreate.as_view()),
    path('comunidades/<int:pk>/', ComunidadDetail.as_view()),

    # Crud propiedades
    path('propiedades/', PropiedadListCreate.as_view()),
    path('propiedades/<int:pk>/', PropiedadDetail.as_view()),

    # Crud RolComunidades
    path('roles-comunidad/', RolComunidadListCreate.as_view()),
    path('roles-comunidad/<int:pk>/', RolComunidadDetail.as_view()),

    # Crud comunicado
    path('comunicados/', ComunicadoListCreate.as_view()),
    path('comunicados/<int:pk>/', ComunicadoDetail.as_view()),

    # Crud comunicado Usuario
    path('comunicadousuario/', ComunicadoUsuarioListCreate.as_view()),
    path('comunicadousuario/<int:pk>/', ComunicadoUsuarioDetail.as_view()),

    # Crud informacion
    path('informaciones/', InformacionListCreate.as_view()),
    path('informaciones/<int:pk>/', InformacionDetail.as_view()),

    # Crud incidencias
    path('incidencias/', IncidenciaListCreate.as_view()),
    path('incidencias/<int:pk>/', IncidenciaDetail.as_view()),
    path('incicambiarestado/<int:pk>/', CambiarStadoIncidencia.as_view()),

    # Crud convocatorias
    path('convocatorias/', ConvocatoriaListCreate.as_view()),
    path('convocatorias/<int:pk>/', ConvocatoriaDetail.as_view()),

    # Crud actas
    path('actas/', ActaListCreate.as_view()),
    path('actas/<int:pk>/', ActaDetail.as_view()),

    # Crud asistencia
    path('asistencia/', AsistenciaListCreate.as_view()),
    path('asistencia/<int:pk>/', AsistenciaDetail.as_view()),

    # Crud orden dia
    path('puntos/', OrdenDiaListCreate.as_view()),
    path('puntos/<int:pk>/', OrdenDiaDetail.as_view()),

    # Crud votacion
    path('votaciones/', VotacionListCreate.as_view()),
    path('votaciones/<int:pk>/', VotacionDetail.as_view()),

    # Crud voto
    path('votos/', VotoListCreate.as_view()),
    path('votos/<int:pk>/', VotoDetail.as_view()),

    # Comunicados sin leer
    path('sinleer/', MensajesLeidos.as_view()),

    path('usuarios_comunicado/', UsuariosEnviarComunicado.as_view()),
]