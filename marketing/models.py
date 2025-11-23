from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


# Seccion nuestros servicios
class Servicio(models.Model):
    # -- campos de cards --
    titulo = models.CharField(max_length=100, verbose_name="Título del Servicio")
    slug = models.SlugField(unique=True, blank=True, help_text="Identificador para la URL")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden de aparición", help_text="Menor número aparece primero (ej: 1, 2, 3...)")
    imagen_card = models.ImageField(upload_to='servicios/cards/', verbose_name="Imagen Pequeña")
    descripcion_corta = models.TextField(verbose_name="Descripción Corta (card)")
    
    # -- campos de pagina detalle --
    # Banner principal (puede ser diferente a la de la card)
    imagen_banner = models.ImageField(upload_to='servicios/banners/', blank=True, null=True)
    
    # Sección: Summary
    resumen = models.TextField(verbose_name="Summary / Resumen")

    # Sección: What you get (Al tener viñetas y negritas, mejor usar RichText)
    que_obtienes = CKEditor5Field(verbose_name="What you get / Qué obtienes")

    # Sección: Why it matters
    por_que_importa = models.TextField(verbose_name="Why it matters / Por qué importa")

    # Sección: How it works (Pasos 1, 2, 3...)
    como_funciona = CKEditor5Field(verbose_name="How it works / Cómo funciona")

    # Sección: Optional Add-ons
    adicionales = CKEditor5Field(verbose_name="Optional Add-ons", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['orden']

    def __str__(self):
        return self.titulo

class CategoriaNoticia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría de Noticia"
        verbose_name_plural = "Categorías de Noticias"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Noticia(models.Model):
    # Relación: Una noticia pertenece a una categoría
    categoria = models.ForeignKey(
        CategoriaNoticia, 
        on_delete=models.SET_NULL, # Si borro la categoría, la noticia queda sin categoría (no se borra)
        null=True, 
        related_name='noticias',
        verbose_name="Categoría"
    )

    titulo = models.CharField(max_length=200, verbose_name="Título de la Noticia")
    slug = models.SlugField(unique=True, blank=True)
    
    # Autor (Opcional: puede ser texto simple o relación con User)
    autor = models.CharField(max_length=100, default="Grupo Reina", verbose_name="Autor")
    
    # Fechas
    fecha_publicacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Publicación")

    # Multimedia
    imagen_card = models.ImageField(upload_to='noticias/cards/', verbose_name="Imagen Pequeña (Card)")
    imagen_banner = models.ImageField(upload_to='noticias/banners/', blank=True, null=True, verbose_name="Banner Grande")

    # Contenido
    resumen = models.TextField(max_length=400, verbose_name="Resumen corto (Intro)")
    contenido = CKEditor5Field(verbose_name="Contenido Completo")

    publicado = models.BooleanField(default=True, verbose_name="¿Publicado?")
    es_destacada = models.BooleanField(default=False, verbose_name="¿Es Destacada?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_publicacion'] # Las más nuevas primero
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    
class CategoriaInvestigacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría de Investigación"
        verbose_name_plural = "Categorías de Investigaciones"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Investigacion(models.Model):
    categoria = models.ForeignKey(
        CategoriaInvestigacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='investigaciones',
        verbose_name="Línea de Investigación"
    )

    titulo = models.CharField(max_length=200, verbose_name="Título de la Investigación")
    slug = models.SlugField(unique=True, blank=True)
    autor = models.CharField(max_length=100, default="Grupo Reina", verbose_name="Investigador/Autor")
    fecha_publicacion = models.DateField(verbose_name="Fecha de Publicación")

    # Multimedia
    imagen_card = models.ImageField(upload_to='investigaciones/cards/', verbose_name="Imagen Pequeña (Card)")
    imagen_banner = models.ImageField(upload_to='investigaciones/banners/', blank=True, null=True, verbose_name="Banner Grande")
    
    archivo_pdf = models.FileField(upload_to='investigaciones/documentos/', blank=True, null=True, verbose_name="PDF Completo (Opcional)")

    # Contenido
    resumen = models.TextField(max_length=500, verbose_name="Resumen Ejecutivo")
    contenido = CKEditor5Field(verbose_name="Detalles de la Investigación", config_name='extends')

    # Estados
    publicado = models.BooleanField(default=True)
    es_destacada = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = "Investigación"
        verbose_name_plural = "Investigaciones"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    
class Certificacion(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Certificación/Logro")
    descripcion = models.TextField(max_length=300, blank=True, verbose_name="Descripción Corta")
    
    logo = models.ImageField(upload_to='certificaciones/logos/', verbose_name="Logo o Ícono")
    url_validacion = models.URLField(blank=True, null=True, verbose_name="Enlace de Verificación (URL)")

    orden = models.PositiveIntegerField(default=0, help_text="1 aparece primero, 2 después...")
    es_visible = models.BooleanField(default=True, verbose_name="¿Visible en la web?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden'] 
        verbose_name = "Certificación / Logro"
        verbose_name_plural = "Certificaciones y Logros"

    def __str__(self):
        return self.nombre
    

class Testimonio(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='testimonios',
        verbose_name="Usuario que comenta"
    )

    contenido = models.TextField(max_length=300, verbose_name="Reseña / Opinión")
    cargo_empresa = models.CharField(max_length=100, blank=True, verbose_name="Cargo / Empresa (Opcional)")
    es_visible = models.BooleanField(default=False, verbose_name="¿Aprobado para mostrar?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 
        verbose_name = "Testimonio / Reseña"
        verbose_name_plural = "Testimonios y Reseñas"

    def __str__(self):
        return f"Opinión de {self.usuario.get_full_name() or self.usuario.username}"
    
    
class CategoriaBlog(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría de Blog"
        verbose_name_plural = "Categorías del Blog"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Blog(models.Model):
    categoria = models.ForeignKey(CategoriaBlog, on_delete=models.SET_NULL, null=True, related_name='posts')
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    autor = models.CharField(max_length=100, default="Grupo Reina") # O ForeignKey a User
    fecha_publicacion = models.DateField(auto_now_add=True)

    imagen_card = models.ImageField(upload_to='blog/cards/', verbose_name="Imagen Card")
    imagen_banner = models.ImageField(upload_to='blog/banners/', blank=True, null=True, verbose_name="Banner")

    resumen = models.TextField(max_length=400)
    contenido = CKEditor5Field(verbose_name="Contenido del Artículo", config_name='extends')

    # Estados
    publicado = models.BooleanField(default=True)
    es_destacado = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = "Artículo de Blog"
        verbose_name_plural = "Blog"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    
class Protocolo(models.Model):
    titulo = models.CharField(max_length=150, verbose_name="Nombre del Cultivo (ej: Batata)")
    slug = models.SlugField(unique=True, blank=True)
    

    imagen_card = models.ImageField(upload_to='protocolos/cards/', verbose_name="Foto del Cultivo")

    descripcion_tecnica = models.TextField(max_length=500, verbose_name="Descripción Técnica / Intro")
    resultados = models.TextField(max_length=300, blank=True, verbose_name="Resultados Esperados")
    contenido = CKEditor5Field(verbose_name="Pasos del Protocolo", config_name='extends')

    archivo_pdf = models.FileField(
        upload_to='protocolos/documentos/', 
        verbose_name="PDF Descargable",
        help_text="Este es el archivo que bajará el usuario al dar clic en 'Descargar Protocolo'"
    )
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en la rejilla")
    es_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden']
        verbose_name = "Protocolo de Cultivo"
        verbose_name_plural = "Protocolos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo