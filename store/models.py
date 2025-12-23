from django.db import models
from django.conf import settings
from marketing.models import Categoria 
from django.utils.text import slugify
from marketing.mixins import WebPConverterMixin


class Producto(WebPConverterMixin, models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, limit_choices_to={'tipo': 'PRODUCTO'}, related_name='productos')
    nombre = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    es_destacado = models.BooleanField(default=False)
    imagen_principal = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    # Sistema de Recomendación simple (Productos relacionados)
    relacionados = models.ManyToManyField('self', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)[:255]
        # Solo llamas a la función mágica pasándole el NOMBRE del campo
        if self.imagen_principal:
            self.convertir_imagen_a_webp('imagen_principal')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
class TarifaEnvio(models.Model):
    ciudad = models.CharField(max_length=100, unique=True, help_text="Ciudad o Municipio destino")
    departamento = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo envío estándar")
    precio_extra_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Costo extra por producto después de X cantidad")

    def __str__(self):
        return f"{self.ciudad} - ${self.precio_base}"

class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto') # Evita duplicados en la BD

class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True) # Para usuarios no logueados
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

class Direccion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='direcciones')
    nombre_completo = models.CharField("Quien recibe", max_length=150)
    direccion = models.CharField("Dirección exacta", max_length=255)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    referencia = models.CharField(max_length=255, blank=True, null=True, help_text="Apto, color casa, etc.")
    es_principal = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.es_principal:
            Direccion.objects.filter(usuario=self.usuario, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ciudad} - {self.direccion}"

class Pedido(models.Model):
    ESTADOS = [('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('ENVIADO', 'Enviado'), ('CANCELADO', 'Cancelado')]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    transaccion_id = models.CharField(max_length=100, blank=True, null=True) 
    metodo_pago = models.CharField(max_length=50, blank=True, default='PENDIENTE')
    created_at = models.DateTimeField(auto_now_add=True)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Guardar precio al momento de compra