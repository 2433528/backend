from rest_framework.permissions import BasePermission

class EsGestor(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('comunicados.gestor')
    
