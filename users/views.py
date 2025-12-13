from rest_framework import generics, status, serializers, viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.conf import settings
from .permissions import IsAdministrador
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Importaciones de Spectacular
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    UserRegisterSerializer, 
    UserProfileSerializer,
    RoleSerializer, 
    UserRoleAssignSerializer, 
    PermissionSerializer, 
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer
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
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo de cambio de pass: {e}")

            return Response(
                {"detail": "Contraseña actualizada correctamente."}, 
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# A. Vista para Crear/Editar los ROLES (Grupos) y sus Permisos
@extend_schema(tags=['Gestión de Roles (Admin)'])
class RoleManagementViewSet(viewsets.ModelViewSet):
    """
    CRUD de Roles. Permite crear nuevos roles (ej: 'Analista') y definir sus permisos.
    """
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdministrador]

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
    summary="Solicitar recuperación de contraseña",
    description="Envía un correo con un link/token al usuario si el email existe.",
    request=PasswordResetRequestSerializer,
    responses={200: OpenApiResponse(description="Correo enviado (o simulado si no existe el user).")}
)
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny] # Cualquiera puede pedir recuperar su cuenta

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Buscamos el usuario (Si no existe, no decimos nada por seguridad)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            
            # 1. Generar Token y UID
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # 2. Crear Link (Ajusta esto a la URL de tu Frontend en React/Angular)
            # Ejemplo: https://mitienda.com/reset-password/MTU/asz-123...
            # Por ahora usaremos una URL genérica de ejemplo:
            domain = "http://127.0.0.1:8000" # Cambiar por tu dominio real
            link = f"{domain}/api/usuarios/password-reset/{uidb64}/{token}/"
            
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
                return Response({'error': 'Error enviando el correo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Si el correo existe, recibirás un enlace de recuperación.'}, status=status.HTTP_200_OK)

# B. Confirmar y Cambiar Contraseña
@extend_schema(
    tags=['Autenticación'],
    summary="Confirmar nueva contraseña",
    description="Recibe el token, el uidb64 (del correo) y la nueva contraseña para efectuar el cambio.",
    request=SetNewPasswordSerializer,
    responses={200: OpenApiResponse(description="Contraseña restablecida exitosamente.")}
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