from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet, 
    CarritoViewSet, 
    PedidoViewSet, 
    FavoritoViewSet,
    DireccionViewSet
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'carrito', CarritoViewSet, basename='carrito')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'favoritos', FavoritoViewSet, basename='favorito')
router.register(r'direcciones', DireccionViewSet, basename='direccion')

urlpatterns = [
    path('', include(router.urls)),
]