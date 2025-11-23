from rest_framework import viewsets
from .models import Servicio, AliadoCertificacion, Testimonio, Noticia
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    ServicioSerializer, AliadoSerializer, 
    TestimonioSerializer, NoticiaSerializer
)

@extend_schema_view(
    list=extend_schema(summary="Listar servicios", description="Muestra los servicios públicos."),
    retrieve=extend_schema(summary="Ver detalle de servicio"),
    create=extend_schema(summary="Crear nuevo servicio", description="[Requiere Auth] Crea un servicio nuevo."),
    update=extend_schema(summary="Actualizar servicio", description="[Requiere Auth] Reemplaza toda la info del servicio."),
    partial_update=extend_schema(summary="Actualizar parcialmente", description="[Requiere Auth] Actualiza campos específicos."),
    destroy=extend_schema(summary="Eliminar servicio", description="[Requiere Auth] Borra el servicio permanentemente.")
)
class ServicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Servicio.objects.all().order_by('orden')
    serializer_class = ServicioSerializer

@extend_schema_view(
    list=extend_schema(summary="Listar aliados y certificaciones", description="Muestra los logos de ICA, ISO, etc."),
    retrieve=extend_schema(summary="Ver detalle de aliado")
)
class AliadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AliadoCertificacion.objects.all()
    serializer_class = AliadoSerializer

@extend_schema_view(
    list=extend_schema(summary="Listar testimonios activos", description="Solo devuelve testimonios marcados como visibles en el admin."),
    retrieve=extend_schema(summary="Ver testimonio individual")
)
class TestimonioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Testimonio.objects.filter(activo=True) # Solo mostramos los activos
    serializer_class = TestimonioSerializer

@extend_schema_view(
    list=extend_schema(summary="Listar noticias publicadas", description="Noticias ordenadas por fecha reciente. Soporta paginación."),
    retrieve=extend_schema(summary="Leer noticia completa", description="Busca la noticia por su slug (URL amigable).")
)
class NoticiaViewSet(viewsets.ReadOnlyModelViewSet):
    # Solo noticias publicadas y ordenadas por fecha
    queryset = Noticia.objects.filter(publicado=True).order_by('-fecha_publicacion')
    serializer_class = NoticiaSerializer
    lookup_field = 'slug' # Para que la URL sea /noticias/mi-titulo-genial/ en vez de un ID número