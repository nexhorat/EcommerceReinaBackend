from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicioViewSet, 
    NoticiaViewSet, 
    InvestigacionViewSet, 
    CertificacionViewSet,
    TestimonioViewSet,
    BlogViewSet,
    ProtocoloViewSet,
    CategoriaViewSet
)

# El Router crea las URLs automáticamente (ej: /servicios/, /noticias/)
router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'noticias', NoticiaViewSet, basename='noticia')
router.register(r'investigaciones', InvestigacionViewSet, basename='investigacion')
router.register(r'certificaciones', CertificacionViewSet, basename='certificacion')
router.register(r'testimonios', TestimonioViewSet, basename='testimonio')
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'protocolos', ProtocoloViewSet, basename='protocolo')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

urlpatterns = [
    path('', include(router.urls)),
]