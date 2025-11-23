from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet, AliadoViewSet, TestimonioViewSet, NoticiaViewSet

# El Router crea las URLs automáticamente (ej: /servicios/, /noticias/)
router = DefaultRouter()
router.register(r'servicios', ServicioViewSet)
router.register(r'aliados', AliadoViewSet)
router.register(r'testimonios', TestimonioViewSet)
router.register(r'noticias', NoticiaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]