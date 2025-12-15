from rest_framework import permissions

class IsDespachadorOrAdmin(permissions.BasePermission):
    """
    Permite acceso a Despachadores o Administradores (Ya lo tenías para Pedidos).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or 
            request.user.groups.filter(name__in=['Administrador', 'Despachador']).exists()
        )

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite lectura (GET) a cualquier usuario (incluso anónimo).
    Pero escritura (POST, PUT, DELETE) solo a Administradores.
    """
    def has_permission(self, request, view):
        # 1. Si es lectura (GET, HEAD, OPTIONS), dejar pasar a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 2. Si es escritura, verificar que sea Admin
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()
        )