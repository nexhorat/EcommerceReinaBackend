from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicioViewSet, 
    NoticiaViewSet, 
    CategoriaNoticiaViewSet, 
    InvestigacionViewSet, 
    CategoriaInvestigacionViewSet, 
    CertificacionViewSet,
    TestimonioViewSet,
    BlogViewSet,
    CategoriaBlogViewSet,
    ProtocoloViewSet
)

# El Router crea las URLs automáticamente (ej: /servicios/, /noticias/)
router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'noticias-categorias', CategoriaNoticiaViewSet, basename='noticia-categoria')
router.register(r'noticias', NoticiaViewSet, basename='noticia')
router.register(r'investigaciones-categorias', CategoriaInvestigacionViewSet, basename='investigacion-categoria')
router.register(r'investigaciones', InvestigacionViewSet, basename='investigacion')
router.register(r'certificaciones', CertificacionViewSet, basename='certificacion')
router.register(r'testimonios', TestimonioViewSet, basename='testimonio')
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'blog-categorias', CategoriaBlogViewSet, basename='blog-categoria')
router.register(r'protocolos', ProtocoloViewSet, basename='protocolo')

urlpatterns = [
    path('', include(router.urls)),
]