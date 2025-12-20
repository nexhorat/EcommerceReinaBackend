from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import (
    Servicio, 
    Noticia, 
    Investigacion,  
    Certificacion, 
    Testimonio, 
    Blog, 
    Protocolo,
    Categoria
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'tipo']

class ServicioCardSerializer(serializers.ModelSerializer):
    """
    Serializador optimizado para la lista (Landing Page).
    Solo envía la información visual de la tarjeta.
    """
    
    class Meta:
        model = Servicio
        fields = [
            'id', 
            'titulo', 
            'slug', 
            'imagen_card', 
            'descripcion_corta',
            'orden'
        ]

class ServicioDetailSerializer(serializers.ModelSerializer):
    """
    Serializador completo para la página de detalle.
    Incluye todo el contenido enriquecido (Rich Text).
    """
    class Meta:
        model = Servicio
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class NoticiaCardSerializer(serializers.ModelSerializer):
    # Truco: Traer el nombre de la categoría en lugar del ID para mostrarlo bonito en la card
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'slug', 'fecha_publicacion', 
            'imagen_card', 'resumen', 'categoria', 'categoria_nombre', 'autor'
        ]

class NoticiaDetailSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Noticia
        fields = '__all__' 
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'fecha_publicacion']


class InvestigacionCardSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Investigacion
        fields = [
            'id', 'titulo', 'slug', 'fecha_publicacion', 
            'imagen_card', 'resumen', 'categoria_nombre', 'autor'
        ]

class InvestigacionDetailSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Investigacion
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CertificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificacion
        fields = '__all__'

class TestimonioSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_foto = serializers.SerializerMethodField()

    class Meta:
        model = Testimonio
        fields = [
            'id',
            'contenido',
            'cargo_empresa',
            'usuario_nombre',
            'usuario_foto',
            'created_at',
            'es_visible'
        ]
        read_only_fields = ['id', 'created_at', 'es_visible']

    @extend_schema_field(str)
    def get_usuario_foto(self, obj):
        request = self.context.get('request')
        if obj.usuario.foto_perfil and hasattr(obj.usuario.foto_perfil, 'url'):
            return request.build_absolute_uri(obj.usuario.foto_perfil.url)
        return None
    
class TestimonioAdminSerializer(TestimonioSerializer):
    """
    Serializador ADMIN:
    - Hereda todo del anterior.
    - Pero SOBRESCRIBE Meta para sacar 'es_visible' de read_only.
    """

    es_visible = serializers.BooleanField(read_only=False)
    
    class Meta(TestimonioSerializer.Meta):
        # Mantenemos los mismos campos
        fields = TestimonioSerializer.Meta.fields
        # Quitamos 'es_visible' de solo lectura para que Swagger permita editarlo
        read_only_fields = ['id', 'created_at']

class BlogCardSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_card = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Blog
        fields = ['id', 'titulo', 'slug', 'fecha_publicacion', 'imagen_card', 'resumen', 'categoria_nombre', 'autor']

class BlogDetailSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at']

class ProtocoloCardSerializer(serializers.ModelSerializer):

    imagen_card = serializers.ImageField(required=False, allow_null=True)
    archivo_pdf = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Protocolo
        fields = ['id', 'titulo', 'slug', 'imagen_card', 'orden']

class ProtocoloDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocolo
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at']