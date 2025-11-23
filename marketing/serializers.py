from rest_framework import serializers
from .models import Servicio, AliadoCertificacion, Testimonio, Noticia, CategoriaNoticia

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'titulo', 'descripcion_corta', 'imagen', 'orden']

class AliadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AliadoCertificacion
        fields = ['id', 'nombre', 'logo', 'url_externa']

class TestimonioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonio
        fields = ['id', 'nombre_cliente', 'cargo_empresa', 'texto', 'foto']

class CategoriaNoticiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaNoticia
        fields = ['id', 'nombre', 'slug']

class NoticiaSerializer(serializers.ModelSerializer):
    # Esto hace que en vez de salir solo el ID de la categoría, salga el objeto completo
    categoria = CategoriaNoticiaSerializer(read_only=True) 
    
    class Meta:
        model = Noticia
        fields = ['id', 'titulo', 'slug', 'categoria', 'imagen_portada', 'contenido', 'fecha_publicacion', 'es_destacada']