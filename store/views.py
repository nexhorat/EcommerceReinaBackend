from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .permissions import IsAdminOrReadOnly, IsDespachadorOrAdmin 

from .models import Producto, Carrito, ItemCarrito, Pedido, DetallePedido, Favorito, Direccion, TarifaEnvio
from .serializers import (
    ProductoCardSerializer, ProductoDetailSerializer, 
    CarritoSerializer, ItemCarritoSerializer, 
    PedidoSerializer, FavoritoSerializer, DireccionSerializer, ErrorResponseSerializer
)
from store import serializers

@extend_schema(tags=['Tienda - Productos'])
class ProductoViewSet(viewsets.ModelViewSet): # <--- CAMBIO: ModelViewSet habilita POST/PUT/DELETE
    queryset = Producto.objects.all().order_by('-es_destacado', '-id')
    
    # PERMISOS: Admin edita, el mundo ve
    permission_classes = [IsAdminOrReadOnly] 

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria', 'es_destacado']
    search_fields = ['nombre', 'descripcion']
    lookup_field = 'slug'

    def get_serializer_class(self):
        # Usamos el DetailSerializer para ver uno solo o para editar/crear (para ver todos los campos)
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
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
        responses={
            200: CarritoSerializer,
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Stock insuficiente o datos inválidos"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="Producto no encontrado")
        }
    )
    @action(detail=False, methods=['post'], url_path='agregar')
    def agregar_item(self, request):
        cart = self._get_cart(request)
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))

        # get_object_or_404 lanza excepción estándar si falla
        producto = get_object_or_404(Producto, id=producto_id)

        # Verificar stock
        if producto.stock < cantidad:
            # REEMPLAZO: raise ValidationError en lugar de return Response manual
            raise ValidationError({"detail": f"No hay suficiente stock. Disponible: {producto.stock}"})

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

@extend_schema(tags=['Tienda - Direcciones'])
class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Direccion.objects.none()
        
        return Direccion.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Asignar usuario automáticamente
        serializer.save(usuario=self.request.user)

@extend_schema(tags=['Tienda - Pedidos'])
class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post'] # No permitir editar/borrar pedidos por API pública

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Pedido.objects.none()
        
        return Pedido.objects.filter(usuario=self.request.user).order_by('-created_at')

    @extend_schema(
        summary="Checkout (Crear Pedido)",
        description="Crea un pedido validando stock y calculando envío.",
        responses={
            201: PedidoSerializer,
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Error de validación (Carrito vacío, stock insuficiente, etc)"),
            404: OpenApiResponse(response=ErrorResponseSerializer, description="Dirección o recurso no encontrado"),
            500: OpenApiResponse(response=ErrorResponseSerializer, description="Error interno del servidor")
        }
    )
    def create(self, request, *args, **kwargs):
        # 1. Validar carrito
        try:
            carrito = Carrito.objects.get(usuario=request.user)
        except Carrito.DoesNotExist:
            raise ValidationError({"detail": "El carrito no existe o está vacío."})
        
        items = carrito.items.all()
        if not items.exists():
            raise ValidationError({"detail": "El carrito está vacío, agrega productos antes de pagar."})

        # 2. Validar Dirección
        direccion_id = request.data.get('direccion_id')
        if not direccion_id:
            raise ValidationError({"direccion_id": "Este campo es obligatorio."})
        
        direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)

        # 3. Calcular Costo de Envío
        try:
            tarifa = TarifaEnvio.objects.get(ciudad__iexact=direccion.ciudad)
            costo_envio = tarifa.precio_base
            
            cantidad_total = sum(item.cantidad for item in items)
            if cantidad_total > 5:
                extra = (cantidad_total - 5) * tarifa.precio_extra_producto
                costo_envio += extra
                
        except TarifaEnvio.DoesNotExist:
            raise ValidationError({"detail": f"Lo sentimos, no tenemos cobertura configurada para {direccion.ciudad}"})

        # 4. Crear Pedido (Transacción Atómica)
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=request.user,
                direccion_envio=direccion,
                estado='PENDIENTE',
                metodo_pago=request.data.get('metodo_pago', 'PENDIENTE'),
                costo_envio=costo_envio,
                subtotal=0,
                total=0
            )

            subtotal_acumulado = 0
            for item in items:
                producto_actual = Producto.objects.select_for_update().get(id=item.producto.id)

                if producto_actual.stock < item.cantidad:
                    raise ValidationError({
                        "detail": f"Stock insuficiente para el producto {producto_actual.nombre}. Disponible: {producto_actual.stock}"
                    })
                
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto_actual,
                    cantidad=item.cantidad,
                    precio_unitario=producto_actual.precio
                )
                
                # Descontar inventario
                producto_actual.stock -= item.cantidad
                producto_actual.save()
                
                subtotal_acumulado += item.cantidad * producto_actual.precio

            # Totales Finales
            pedido.subtotal = subtotal_acumulado
            pedido.total = subtotal_acumulado + costo_envio
            pedido.save()

            # Vaciar carrito
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