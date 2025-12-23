from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from .permissions import IsAdministrador
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

# Importaciones de Spectacular
from drf_spectacular.utils import extend_schema, OpenApiResponse
from store.serializers import ErrorResponseSerializer

from .serializers import (
    UserRegisterSerializer, 
    UserProfileSerializer,
    RoleSerializer, 
    UserRoleAssignSerializer, 
    PermissionSerializer, 
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()

@extend_schema(
    tags=['Autenticación'],
    summary="Registrar Usuario",
    responses={
        201: UserRegisterSerializer,
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Email duplicado o contraseña débil"),
        500: OpenApiResponse(response=ErrorResponseSerializer, description="Error interno")
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
    summary="Login (Tokens)",
    responses={
        200: OpenApiResponse(description="Tokens JWT generados"),
        401: OpenApiResponse(response=ErrorResponseSerializer, description="Credenciales inválidas"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Faltan datos")
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(
    tags=['Autenticación'],
    summary="Perfil de Usuario",
    methods=["GET", "PUT", "PATCH"],
    responses={
        200: UserProfileSerializer,
        401: OpenApiResponse(response=ErrorResponseSerializer, description="Token inválido o expirado"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Datos de perfil inválidos")
    }
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user
    
    
# A. Vista para Crear/Editar los ROLES (Grupos) y sus Permisos
@extend_schema(tags=['Gestión de Roles (Admin)'])
class RoleManagementViewSet(viewsets.ModelViewSet):
    """
    CRUD de Roles. Permite crear nuevos roles (ej: 'Analista') y definir sus permisos.
    """
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdministrador]

    @extend_schema(
        summary="Listar Permisos Disponibles",
        responses={200: PermissionSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def permisos_disponibles(self, request):
        """Lista todos los permisos del sistema para que el Admin elija cuáles asignar."""
        # Filtramos solo permisos de nuestras apps para no ensuciar la lista
        apps_relevantes = ['store', 'marketing', 'users']
        permisos = Permission.objects.filter(content_type__app_label__in=apps_relevantes)
        serializer = PermissionSerializer(permisos, many=True)
        return Response(serializer.data)

# B. Vista para Asignar esos Roles a los Usuarios
@extend_schema(tags=['Gestión de Usuarios (Admin)'])
class UserRoleAssignmentViewSet(viewsets.ModelViewSet):
    """
    Solo para cambiar los roles de un usuario existente.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserRoleAssignSerializer
    permission_classes = [IsAdministrador]
    http_method_names = ['get', 'patch'] # Solo ver y modificar parcialmente

# A. Solicitar Link de Recuperación
@extend_schema(
    tags=['Autenticación'],
    summary="Recuperar Contraseña (Solicitud)",
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(description="Siempre retorna 200 para evitar enumeración de usuarios."),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Email inválido")
    }
)
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny] # Cualquiera puede pedir recuperar su cuenta

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Buscamos el usuario (Si no existe, no decimos nada por seguridad)
        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            user = user_qs.first()
            
            # 1. Generar Token y UID
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # 2. Crear Link (Ajusta esto a la URL de tu Frontend en React/Angular)
            # Ajustar dominio según variable de entorno en prod
            domain = getattr(settings, 'FRONTEND_URL', "http://localhost:3000")
            link = f"{domain}/reset-password/{uidb64}/{token}"
            
            # 3. Enviar Correo
            try:
                html_content = render_to_string('emails/password_reset.html', {
                    'nombre': user.first_name,
                    'link': link
                })
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(
                    'Restablecer Contraseña - Ecommerce Reina',
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
            except Exception as e:
                logger.error(f"Fallo envío email recuperación para {email}: {str(e)}")

        return Response({'detail': 'Si el correo existe, recibirás un enlace de recuperación.'}, status=status.HTTP_200_OK)

# B. Confirmar y Cambiar Contraseña
@extend_schema(
    tags=['Autenticación'],
    summary="Confirmar nueva contraseña",
    description="Recibe el token, el uidb64 (del correo) y la nueva contraseña para efectuar el cambio.",
    request=SetNewPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Contraseña actualizada"),
        400: OpenApiResponse(response=ErrorResponseSerializer, description="Token inválido o passwords no coinciden")
    }
)
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # El método save() del serializer ya hace el user.set_password()
        serializer.save() 

        return Response({'detail': 'Contraseña restablecida exitosamente.'}, status=status.HTTP_200_OK)