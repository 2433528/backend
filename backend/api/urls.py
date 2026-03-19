from django.urls import path
from .views import *

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view()),
    path('refresh/', MyTokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('getuser/', get_user),

    # Conseguir clave publica
    path('api/webpush-key/', vapid_key),

    # Crud usuarios
    path('usuarios/', UsuarioListCreate.as_view()),
    path('usuarios/<int:pk>/', UsuarioDetail.as_view()),

    # Crud comunidades
    path('comunidades/', ComunidadListCreate.as_view()),
    path('comunidades/<int:pk>/', ComunidadDetail.as_view()),

    # Crud propiedades
    path('propiedades/', PropiedadListCreate.as_view()),
    path('propiedades/<int:pk>/', PropiedadDetail.as_view()),

    # Crud comunicado
    path('comunicados/', ComunicadoListCreate.as_view()),
    path('comunicados/<int:pk>/', ComunicadoDetail.as_view()),

    # Crud informacion
    path('propiedades/', InformacionListCreate.as_view()),
    path('propiedades/<int:pk>/', InformacionDetail.as_view()),

    # Crud incidencias
    path('incidencias/', IncidenciaListCreate.as_view()),
    path('incidencias/<int:pk>/', IncidenciaDetail.as_view()),

    # Crud actas
    path('incidencias/', IncidenciaListCreate.as_view()),
    path('incidencias/<int:pk>/', IncidenciaDetail.as_view()),

    # Crud asistencia
    path('asistencia/', AsistenciaListCreate.as_view()),
    path('asistencia/<int:pk>/', AsistenciaDetail.as_view()),

    # Crud orden dia
    path('incidencias/', OrdenDiaListCreate.as_view()),
    path('incidencias/<int:pk>/', OrdenDiaDetail.as_view()),

    # Crud votacion
    path('incidencias/', VotacionListCreate.as_view()),
    path('incidencias/<int:pk>/', VotacionDetail.as_view()),

    # Crud voto
    path('incidencias/', VotoListCreate.as_view()),
    path('incidencias/<int:pk>/', VotoDetail.as_view()),
]