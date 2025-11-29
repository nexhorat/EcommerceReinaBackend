from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Producto, Carrito, ItemCarrito, Pedido, DetallePedido, Favorito
from .serializers import (
    ProductoCardSerializer, ProductoDetailSerializer, 
    CarritoSerializer, ItemCarritoSerializer, 
    PedidoSerializer, FavoritoSerializer
)
from store import serializers

@extend_schema(tags=['Tienda - Productos'])
class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.all().order_by('-es_destacado', '-id')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria', 'es_destacado']
    search_fields = ['nombre', 'descripcion']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoCardSerializer

    @action(detail=False, methods=['get'])
    def recomendaciones(self, request):
        """Retorna productos destacados o aleatorios como recomendación."""
        queryset = self.get_queryset().filter(es_destacado=True)[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Tienda - Carrito'])
class CarritoViewSet(viewsets.GenericViewSet):
    """
    Gestiona el carrito del usuario actual.
    No usa ModelViewSet estándar porque la lógica es custom (get_or_create).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CarritoSerializer
    queryset = Carrito.objects.none()

    def _get_cart(self, request):
        cart, _ = Carrito.objects.get_or_create(usuario=request.user)
        return cart

    @extend_schema(responses=CarritoSerializer)
    def list(self, request):
        """Ver el carrito actual"""
        cart = self._get_cart(request)
        serializer = CarritoSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Agregar Item",
        request=ItemCarritoSerializer,
        responses=CarritoSerializer
    )
    @action(detail=False, methods=['post'], url_path='agregar')
    def agregar_item(self, request):
        cart = self._get_cart(request)
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        producto = get_object_or_404(Producto, id=producto_id)

        # Verificar stock
        if producto.stock < cantidad:
            return Response({'error': 'No hay suficiente stock'}, status=400)

        item, created = ItemCarrito.objects.get_or_create(
            carrito=cart, producto=producto,
            defaults={'cantidad': 0}
        )
        item.cantidad += cantidad
        item.save()

        return Response(CarritoSerializer(cart).data)

    @extend_schema(
            summary="Eliminar Item del Carrito", 
            parameters=[OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='ID del Producto a eliminar')]
    )
    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_item(self, request, pk=None):
        """El PK aquí es el ID del PRODUCTO a eliminar, no del Item"""
        cart = self._get_cart(request)
        # Buscamos por producto_id para facilitar al frontend
        item = get_object_or_404(ItemCarrito, carrito=cart, producto_id=pk)
        item.delete()
        return Response(CarritoSerializer(cart).data)

@extend_schema(tags=['Tienda - Pedidos'])
class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post'] # No permitir editar/borrar pedidos por API pública

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Pedido.objects.none()
        
        return Pedido.objects.filter(usuario=self.request.user).order_by('-created_at')

    @extend_schema(summary="Checkout (Crear Pedido desde Carrito)")
    def create(self, request, *args, **kwargs):
        # 1. Obtener carrito
        try:
            carrito = Carrito.objects.get(usuario=request.user)
        except Carrito.DoesNotExist:
            return Response({"error": "El carrito está vacío"}, status=400)

        items = carrito.items.all()
        if not items.exists():
            return Response({"error": "El carrito está vacío"}, status=400)

        # 2. Calcular total y validar stock (Atomic Transaction)
        total = 0
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                total=0, # Se actualiza abajo
                estado='PENDIENTE',
                metodo_pago=request.data.get('metodo_pago', 'PENDIENTE')
            )

            for item in items:
                if item.producto.stock < item.cantidad:
                    raise serializers.ValidationError(f"Stock insuficiente para {item.producto.nombre}")
                
                # Crear detalle
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
                
                # Restar stock
                item.producto.stock -= item.cantidad
                item.producto.save()
                
                total += item.cantidad * item.producto.precio

            pedido.total = total
            pedido.save()

            # 3. Vaciar carrito
            carrito.items.all().delete()

        serializer = self.get_serializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(tags=['Tienda - Favoritos'])
class FavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorito.objects.none()
        
        return Favorito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Evitar duplicados
        producto = serializer.validated_data['producto']
        if Favorito.objects.filter(usuario=self.request.user, producto=producto).exists():
            return # Ya existe, no hacemos nada (o podrías lanzar error)
        serializer.save(usuario=self.request.user)