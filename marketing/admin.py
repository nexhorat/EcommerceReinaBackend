from django.contrib import admin
from .models import Servicio, AliadoCertificacion, Testimonio, CategoriaNoticia, Noticia

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden')
    list_editable = ('orden',) # Permite cambiar el orden rápido sin entrar a editar

@admin.register(AliadoCertificacion)
class AliadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url_externa')

@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'cargo_empresa', 'activo')
    list_filter = ('activo',)
    list_editable = ('activo',)

@admin.register(CategoriaNoticia)
class CategoriaNoticiaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)} # Llena el slug automáticamente al escribir el nombre

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_publicacion', 'publicado', 'es_destacada')
    list_filter = ('categoria', 'publicado', 'es_destacada', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'slug': ('titulo',)}