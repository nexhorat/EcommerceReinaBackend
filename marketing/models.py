from django.db import models
from django.utils import timezone

# Seccion nuestros servicios
class Servicio(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título del Servicio")
    descripcion_corta = models.TextField(verbose_name="Descripción Corta")
    imagen = models.ImageField(upload_to='servicios/', verbose_name="Imagen Principal")
    orden = models.PositiveIntegerField(default=0, help_text="Define el orden de aparición (1, 2, 3...)")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['orden']

    def __str__(self):
        return self.titulo

# Seccion confianza (logos)
class AliadoCertificacion(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre (Ej: ICA, ISO)")
    logo = models.ImageField(upload_to='aliados/', verbose_name="Logo/Sello")
    url_externa = models.URLField(blank=True, null=True, verbose_name="Enlace (Opcional)")
    
    class Meta:
        verbose_name = "Certificación/Aliado"
        verbose_name_plural = "Certificaciones y Aliados"

    def __str__(self):
        return self.nombre

# 3. Seccion testimonios
class Testimonio(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    cargo_empresa = models.CharField(max_length=100, blank=True, help_text="Ej: CEO de GreenLeaf")
    texto = models.TextField(verbose_name="Reseña")
    foto = models.ImageField(upload_to='testimonios/', blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="Mostrar en el sitio")

    def __str__(self):
        return f"{self.nombre_cliente} - {self.cargo_empresa}"

# 4. Seccion noticias
class CategoriaNoticia(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, help_text="Identificador URL (ej: medio-ambiente)")

    def __str__(self):
        return self.nombre

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    categoria = models.ForeignKey(CategoriaNoticia, on_delete=models.PROTECT)
    imagen_portada = models.ImageField(upload_to='noticias/')
    contenido = models.TextField(help_text="Aquí va el cuerpo de la noticia")
    
    # Control de publicación
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    es_destacada = models.BooleanField(default=False, help_text="Si se marca, sale en el banner principal")
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_publicacion'] # Las más recientes primero

    def __str__(self):
         return self.titulo