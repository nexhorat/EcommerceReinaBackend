from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

# Importaciones de Spectacular
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    UserRegisterSerializer, 
    UserProfileSerializer, 
    ChangePasswordSerializer
)

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
    summary="Iniciar Sesión (Obtener Tokens)",
    description="Envía email y password para obtener los tokens 'access' y 'refresh'.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(
    summary="Ver o Editar Mi Perfil",
    description="Permite al usuario logueado ver sus datos, cambiar nombre/teléfono y SUBIR SU FOTO.",
    methods=["GET", "PUT", "PATCH"]
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user
    

@extend_schema(
    summary="Cambiar Contraseña",
    description="Requiere la contraseña anterior y la nueva repetida dos veces.",
    responses={200: {"detail": "Contraseña actualizada correctamente."}}
)
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # 1. Verificar que la contraseña vieja sea correcta
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["La contraseña actual es incorrecta."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Guardar la nueva contraseña
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            
            return Response(
                {"detail": "Contraseña actualizada correctamente."}, 
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)