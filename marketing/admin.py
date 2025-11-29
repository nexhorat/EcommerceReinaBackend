from django.contrib import admin
from .models import (
    Servicio, 
    Noticia, 
    Investigacion, 
    Testimonio,
    Blog,
    Protocolo,
    Categoria
)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden', 'slug', 'created_at')
    list_editable = ('orden',) # Permite cambiar el orden rápido sin entrar a editar
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'slug')
    list_filter = ('tipo',) # Filtro lateral para ver solo noticias, blogs, etc.
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Ahora sí funcionará porque los campos ya existen en el modelo
    list_display = ('titulo', 'categoria', 'fecha_publicacion', 'publicado', 'es_destacada')
    list_editable = ('publicado', 'es_destacada', 'categoria') # Para activar/desactivar rápido sin entrar
    list_filter = ('publicado', 'es_destacada', 'categoria', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Investigacion)
class InvestigacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_publicacion', 'autor', 'publicado')
    list_filter = ('categoria', 'fecha_publicacion', 'publicado')
    search_fields = ('titulo', 'resumen')
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'es_visible', 'created_at')
    list_editable = ('es_visible',)
    list_filter = ('es_visible', 'created_at')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_publicacion', 'autor', 'publicado', 'es_destacado')
    list_editable = ('publicado', 'es_destacado') 
    list_filter = ('categoria', 'publicado', 'es_destacado', 'fecha_publicacion')
    search_fields = ('titulo', 'resumen', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}

@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden', 'es_visible', 'archivo_pdf')
    list_editable = ('orden', 'es_visible')
    search_fields = ('titulo',)
    prepopulated_fields = {'slug': ('titulo',)}

