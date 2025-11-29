from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.conf import settings

# Importaciones de Spectacular
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
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
    responses={
        201: OpenApiResponse(response=UserRegisterSerializer, description="Usuario creado exitosamente (incluye mensaje 'detail')."),
        400: OpenApiResponse(description="Error de validación (email ya existe o contraseña inválida).")
    }
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        response_data = dict(serializer.data)
        
        response_data['detail'] = "Usuario registrado exitosamente."

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

@extend_schema(
    tags=['Autenticación'],
    summary="Iniciar Sesión (Obtener Tokens)",
    description="Envía email y password para obtener los tokens 'access' y 'refresh'.",
    responses={
        200: OpenApiResponse(description="Tokens de acceso y refresco generados correctamente."),
        401: OpenApiResponse(description="Credenciales inválidas (email o contraseña incorrectos).")
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(
    summary="Ver o Editar Mi Perfil",
    description="Permite al usuario logueado ver sus datos, cambiar nombre/teléfono y SUBIR SU FOTO.",
    methods=["GET", "PUT", "PATCH"],
    responses={
        200: UserProfileSerializer,
        401: OpenApiResponse(description="No autenticado. Token faltante o inválido."),
        400: OpenApiResponse(description="Datos de entrada inválidos.")
    }
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user
    

@extend_schema(
    summary="Cambiar Contraseña",
    description="Requiere la contraseña anterior y la nueva repetida dos veces.",
    responses={
        200: inline_serializer(
            name='PasswordChangeResponse',
            fields={
                'detail': serializers.CharField(default="Contraseña actualizada correctamente.")
            }
        )
    }
)
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None 
            
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # 1. Verificar contraseña vieja
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["La contraseña actual es incorrecta."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Guardar nueva contraseña
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            
            # 3. ENVIAR CORREO DE NOTIFICACIÓN
            try:
                send_mail(
                    subject='Alerta de Seguridad: Tu contraseña ha cambiado',
                    message=f'Hola {self.object.first_name}, te informamos que tu contraseña fue actualizada exitosamente.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.object.email],
                    fail_silently=FalseTrue,
                )
            except Exception as e:
                print(f"Error enviando correo de cambio de pass: {e}")

            return Response(
                {"detail": "Contraseña actualizada correctamente."}, 
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)