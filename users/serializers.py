from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field

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
        fields = ['id', 'email', 'first_name', 'last_name', 'telefono', 'role', 'foto_perfil']
        read_only_fields = ['id', 'email'] 

    @extend_schema_field(str)
    def get_role(self, obj):
        # Lógica para determinar el rol basado en grupos
        if obj.is_superuser or obj.groups.filter(name='Administrador').exists():
            return 'ADMIN'
        return 'USER'    


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, label="Contraseña actual")
    new_password = serializers.CharField(required=True, write_only=True, label="Nueva contraseña")
    confirm_password = serializers.CharField(required=True, write_only=True, label="Confirmar nueva contraseña")

    def validate(self, attrs):
        
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Las contraseñas nuevas no coinciden."})
        
        user = self.context['request'].user
        try:
            validate_password(attrs['new_password'], user)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs