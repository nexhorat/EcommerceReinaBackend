from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

# Importaciones de Spectacular
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .serializers import UserRegisterSerializer, UserDetailSerializer

User = get_user_model()

@extend_schema(
    tags=['Autenticación'],
    summary="Registrar un nuevo usuario",
    description="Crea un usuario con rol USER por defecto. Requiere email, nombres y contraseña.",
    responses={201: UserRegisterSerializer} # Qué devuelve si sale bien
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

@extend_schema(
    tags=['Autenticación'],
    summary="Obtener perfil del usuario actual (Me)",
    description="Devuelve los datos del usuario logueado basándose en el Token JWT enviado en el Header.",
    # Opcional: Puedes documentar errores específicos
    responses={
        200: UserDetailSerializer,
        401: OpenApiTypes.OBJECT, 
    }
)
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user

@extend_schema(
    tags=['Autenticación'],
    summary="Iniciar Sesión (Obtener Tokens)",
    description="Envía email y password para obtener los tokens 'access' y 'refresh'.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass