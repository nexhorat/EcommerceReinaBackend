from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Producto, Favorito, Carrito, ItemCarrito, Pedido, DetallePedido, Direccion, TarifaEnvio

# --- PRODUCTOS ---
class ProductoCardSerializer(serializers.ModelSerializer):
    """Vista ligera para listas"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'slug', 'precio', 'imagen_principal', 'es_destacado', 'categoria_nombre']

class ProductoDetailSerializer(serializers.ModelSerializer):
    """Vista completa para detalle"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    relacionados = ProductoCardSerializer(many=True, read_only=True) 

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'categoria_nombre']

# --- CARRITO ---
class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoCardSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'subtotal']
        read_only_fields = ['id', 'producto_id']

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_subtotal(self, obj):
        return obj.cantidad * obj.producto.precio

class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'items', 'total'] #  'updated_at'  Asumiendo que agregas updated_at o usas created_at

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total(self, obj):
        return sum(item.cantidad * item.producto.precio for item in obj.items.all())

# --- PEDIDOS ---
class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = ['producto_nombre', 'cantidad', 'precio_unitario']

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'total', 'estado', 'metodo_pago', 'created_at', 'detalles']
        read_only_fields = ['usuario', 'total', 'estado', 'created_at']

# --- FAVORITOS ---
class FavoritoSerializer(serializers.ModelSerializer):
    producto = ProductoCardSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = Favorito
        fields = ['id', 'producto', 'producto_id', 'created_at']
        read_only_fields = ['created_at', 'id', 'producto_id']

class TarifaEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarifaEnvio
        fields = '__all__'

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['id', 'nombre_completo', 'direccion', 'ciudad', 'departamento', 'telefono', 'referencia', 'es_principal']