from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'telefono']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usamos create_user del Manager para que hashee el password
        user = User.objects.create_user(**validated_data)
        return user
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Agregamos los nuevos campos a la lista
        fields = ['id', 'email', 'first_name', 'last_name', 'telefono', 'role', 'foto_perfil', 'recibir_newsletter', 'recibir_ofertas']
        read_only_fields = ['id', 'email', 'role'] 

    @extend_schema_field(str)
    def get_role(self, obj):
        # Lógica para determinar el rol basado en grupos
        if obj.is_superuser or obj.groups.filter(name='Administrador').exists():
            return 'ADMIN'
        return 'USER'    
  
# 1. Para listar los permisos disponibles (necesario para crear roles)
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

# 2. Para Crear/Editar Roles (Grupos) y asignarles permisos
class RoleSerializer(serializers.ModelSerializer):
    # El admin enviará los codenames de los permisos, ej: ["add_blog", "change_pedido"]
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

# 3. Para asignar Roles a Usuarios (Minimalista)
class UserRoleAssignSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'groups']
        read_only_fields = ['id', 'first_name', 'email'] # Solo 'groups' es editable

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')

        # 1. Decodificar el ID del usuario
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Enlace inválido o expirado (UID).')

        # 2. Verificar que el token sea válido para ese usuario
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('El token de restablecimiento es inválido o ha expirado.')

        attrs['user'] = user # Guardamos el usuario para usarlo en el save
        return attrs

    def save(self):
        password = self.validated_data['password']
        user = self.validated_data['user']
        user.set_password(password)
        user.save()
        return user