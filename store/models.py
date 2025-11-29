from django.db import models
from django.conf import settings
from marketing.models import Categoria # Usamos la categoría unificada

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, limit_choices_to={'tipo': 'PRODUCTO'}, related_name='productos')
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    es_destacado = models.BooleanField(default=False)
    imagen_principal = models.ImageField(upload_to='productos/')
    
    # Sistema de Recomendación simple (Productos relacionados)
    relacionados = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.nombre

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

class Pedido(models.Model):
    ESTADOS = [('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('ENVIADO', 'Enviado'), ('CANCELADO', 'Cancelado')]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # Datos de Pasarela
    transaccion_id = models.CharField(max_length=100, blank=True, null=True) # ID de Wompi/MercadoPago
    metodo_pago = models.CharField(max_length=50, blank=True, default='PENDIENTE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Guardar precio al momento de compra