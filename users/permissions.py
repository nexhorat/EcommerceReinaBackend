from rest_framework import permissions

class IsAdministrador(permissions.BasePermission):
    """
    Permite acceso si el usuario es Superuser o pertenece al grupo 'Administrador'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()
        )