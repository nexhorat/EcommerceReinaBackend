from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import filters
from .models import (
    Servicio, 
    Noticia, 
    Investigacion,  
    Certificacion, 
    Testimonio,
    Blog,
    Protocolo,
    Categoria
)
from .serializers import (
    ServicioCardSerializer, 
    ServicioDetailSerializer, 
    NoticiaDetailSerializer, 
    NoticiaCardSerializer, 
    CategoriaSerializer,
    InvestigacionCardSerializer,
    InvestigacionDetailSerializer,
    CertificacionSerializer,
    TestimonioSerializer,
    BlogCardSerializer,
    BlogDetailSerializer,
    ProtocoloDetailSerializer,
    ProtocoloCardSerializer
)

@extend_schema_view(
    list=extend_schema(
        summary="Listar Categorías",
        description="Obtiene todas las categorías. Filtra por 'tipo' para obtener solo Noticias, Blog, etc.",
        parameters=[
            OpenApiParameter(
                name='tipo', 
                description='Tipo de categoría (NOTICIA, INVESTIGACION, BLOG)', 
                required=False, 
                type=str
            ),
        ]
    ),
    retrieve=extend_schema(summary="Ver Categoría"),
    create=extend_schema(summary="Crear Categoría", description="Solo Admin"),
    update=extend_schema(summary="Editar Categoría", description="Solo Admin"),
    destroy=extend_schema(summary="Eliminar Categoría", description="Solo Admin"),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo'] 

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]




@extend_schema_view(
    # --- LECTURA (Público) ---
    list=extend_schema(
        summary="Listar Servicios (Cards)",
        description="Obtiene la lista ligera para el Landing.",
        responses={200: ServicioCardSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Ver Detalle del Servicio",
        description="Obtiene toda la info completa del servicio por su slug.",
        responses={200: ServicioDetailSerializer}
    ),
    # --- ESCRITURA (Privado - Solo Admin) ---
    create=extend_schema(
        summary="Crear Nuevo Servicio",
        description="Crea un servicio nuevo. Requiere autenticación.",
        responses={201: ServicioDetailSerializer}
    ),
    update=extend_schema(
        summary="Actualizar Servicio (Completo)",
        description="Reemplaza toda la información del servicio.",
        responses={200: ServicioDetailSerializer}
    ),
    partial_update=extend_schema(
        summary="Actualizar Servicio (Parcial)",
        description="Actualiza solo algunos campos del servicio.",
        responses={200: ServicioDetailSerializer}
    ),
    destroy=extend_schema(
        summary="Eliminar Servicio",
        description="Borra un servicio permanentemente.",
    ),
)
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all().order_by('orden')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser] # Para subir imágenes

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicioCardSerializer
        return ServicioDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

@extend_schema_view(
    list=extend_schema(
        summary="Listar Categorías de Noticias",
        description="Devuelve la lista de categorías (ej: Agricultura, Eventos) para llenar el menú de filtros del frontend."
    ),
    retrieve=extend_schema(summary="Ver Categoría Individual"),
    create=extend_schema(summary="Crear Categoría", description="Solo Admin"),
    update=extend_schema(summary="Editar Categoría", description="Solo Admin"),
    destroy=extend_schema(summary="Eliminar Categoría", description="Solo Admin"),
)
class CategoriaNoticiaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    lookup_field = 'slug'
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminUser]


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes] 

@extend_schema_view(
    list=extend_schema(
        summary="Listar Noticias (Cards)",
        description="Obtiene las noticias ordenadas por fecha. Soporta filtrado por categoría.",
        # Documentamos explícitamente que se puede filtrar por 'categoria'
        parameters=[
            OpenApiParameter(name='categoria', description='ID de la categoría para filtrar noticias', required=False, type=int),
            OpenApiParameter(name='es_destacada', description='Filtrar por true/false para mostrar solo destacadas', required=False, type=bool),
        ]
    ),
    retrieve=extend_schema(
        summary="Leer Noticia Completa",
        description="Trae el contenido completo, incluyendo el texto enriquecido (HTML) y el banner."
    ),
    create=extend_schema(summary="Publicar Noticia", description="Solo Admin. Recuerda enviar imagen_card e imagen_banner."),
    update=extend_schema(summary="Editar Noticia", description="Solo Admin."),
    destroy=extend_schema(summary="Eliminar Noticia", description="Solo Admin."),
)
class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all().order_by('-fecha_publicacion')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['categoria', 'es_destacada', 'publicado'] 
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return NoticiaCardSerializer
        return NoticiaDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(summary="Listar Categorías Investigación", description="Para el menú de filtros."),
    create=extend_schema(summary="Crear Categoría Inv.", description="Solo Admin"),
    update=extend_schema(summary="Editar Categoría Inv.", description="Solo Admin"),
    destroy=extend_schema(summary="Eliminar Categoría Inv.", description="Solo Admin"),
)
class CategoriaInvestigacionViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminUser] # Ajusta a AllowAny en get_permissions si quieres lectura pública
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


@extend_schema_view(
    list=extend_schema(
        summary="Listar Investigaciones (Cards)",
        description="Lista ligera. Filtra por ?categoria=ID o ?es_destacada=true",
        parameters=[
            OpenApiParameter(name='categoria', type=int, required=False),
            OpenApiParameter(name='es_destacada', type=bool, required=False),
        ]
    ),
    retrieve=extend_schema(summary="Ver Investigación Completa", description="Incluye PDF y HTML."),
    create=extend_schema(summary="Publicar Investigación", description="Solo Admin. Soporta carga de archivos."),
)
class InvestigacionViewSet(viewsets.ModelViewSet):
    queryset = Investigacion.objects.all().order_by('-fecha_publicacion')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria', 'es_destacada', 'publicado']

    def get_serializer_class(self):
        if self.action == 'list':
            return InvestigacionCardSerializer
        return InvestigacionDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
@extend_schema_view(
    list=extend_schema(summary="Listar Certificaciones", description="Muestra los logos y logros."),
    create=extend_schema(summary="Crear Certificación", description="Sube el logo y opcionalmente la URL de validación."),
    update=extend_schema(summary="Editar Certificación"),
    destroy=extend_schema(summary="Eliminar Certificación"),
)
class CertificacionViewSet(viewsets.ModelViewSet):
    # Solo mostramos las que tengan es_visible=True (opcional, o filtro en frontend)
    queryset = Certificacion.objects.filter(es_visible=True).order_by('orden')
    serializer_class = CertificacionSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        # Cualquiera ve la lista, solo Admin crea/borra
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
@extend_schema_view(
    list=extend_schema(summary="Listar Testimonios Aprobados", description="Muestra solo las reseñas que han sido marcadas como visibles por el admin."),
    create=extend_schema(summary="Crear un Testimonio", description="Requiere estar autenticado (Token). El usuario se asigna automáticamente."),
)
class TestimonioViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
             return Testimonio.objects.filter(es_visible=True)
        return Testimonio.objects.all()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="Listar Blog", parameters=[OpenApiParameter(name='categoria', type=int)]),
    retrieve=extend_schema(summary="Leer Artículo Completo"),
    create=extend_schema(summary="Crear Post", description="Solo Admin"),
)
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-fecha_publicacion')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria', 'es_destacado', 'publicado']

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogCardSerializer
        return BlogDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

class CategoriaBlogViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminUser] # Ajustar si quieres público
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
             return [AllowAny()]
        return [IsAdminUser()]
    

@extend_schema_view(
    list=extend_schema(summary="Listar Protocolos (Grid)", description="Devuelve la lista de cultivos para la rejilla principal."),
    retrieve=extend_schema(summary="Ver Detalle Protocolo (Modal)", description="Devuelve la info técnica y el link del PDF."),
    create=extend_schema(summary="Crear Protocolo", description="Solo Admin. Requiere PDF."),
    update=extend_schema(summary="Editar Protocolo", description="Solo Admin."),
    destroy=extend_schema(summary="Eliminar Protocolo", description="Solo Admin."),
)
class ProtocoloViewSet(viewsets.ModelViewSet):
    queryset = Protocolo.objects.filter(es_visible=True).order_by('orden')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # Buscador por si quieren buscar "Arroz"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['titulo', 'contenido'] 

    def get_queryset(self):
        # Si es admin ve todo (incluso ocultos), si es público solo visibles
        if self.request.user.is_staff:
            return Protocolo.objects.all().order_by('orden')
        return Protocolo.objects.filter(es_visible=True).order_by('orden')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProtocoloCardSerializer
        return ProtocoloDetailSerializer

    def get_permissions(self):
        # Lectura pública, Escritura privada
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]