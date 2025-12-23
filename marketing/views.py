from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from store.serializers import ErrorResponseSerializer
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
    TestimonioAdminSerializer,
    BlogCardSerializer,
    BlogDetailSerializer,
    ProtocoloDetailSerializer,
    ProtocoloCardSerializer
)

# --- PERMISO PERSONALIZADO (Definido al inicio para usar en todo el archivo) ---
class IsGrupoAdministrador(permissions.BasePermission):
    """
    Permite el acceso solo si el usuario pertenece al grupo 'Administrador'
    o es superusuario. Reemplaza la validación de is_staff.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Administrador').exists() or request.user.is_superuser


# --- MIXIN PARA DOCUMENTACIÓN DE ERRORES COMUNES ---
# Define los errores estándar para reutilizarlos en todos los esquemas
common_errors = {
    400: OpenApiResponse(response=ErrorResponseSerializer, description="Error de validación o datos mal formados"),
    401: OpenApiResponse(response=ErrorResponseSerializer, description="No autenticado"),
    403: OpenApiResponse(response=ErrorResponseSerializer, description="No tienes permisos para esta acción"),
    500: OpenApiResponse(response=ErrorResponseSerializer, description="Error interno del servidor")
}

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
        ],
        responses={200: CategoriaSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Categoría",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Crear Categoría", 
        description="Solo Admin",
        responses={201: CategoriaSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Categoría", 
        description="Solo Admin",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Categoría", 
        description="Solo Admin",
        responses={**common_errors}
    ),
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
        return [IsGrupoAdministrador()]


@extend_schema_view(
    # --- LECTURA (Público) ---
    list=extend_schema(
        summary="Listar Servicios (Cards)",
        description="Obtiene la lista ligera para el Landing.",
        responses={200: ServicioCardSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Detalle del Servicio",
        description="Obtiene toda la info completa del servicio por su slug.",
        responses={200: ServicioDetailSerializer, **common_errors}
    ),
    # --- ESCRITURA (Privado - Solo Admin) ---
    create=extend_schema(
        summary="Crear Nuevo Servicio",
        description="Crea un servicio nuevo. Requiere autenticación.",
        responses={201: ServicioDetailSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Actualizar Servicio (Completo)",
        description="Reemplaza toda la información del servicio.",
        responses={200: ServicioDetailSerializer, **common_errors}
    ),
    partial_update=extend_schema(
        summary="Actualizar Servicio (Parcial)",
        description="Actualiza solo algunos campos del servicio.",
        responses={200: ServicioDetailSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Servicio",
        description="Borra un servicio permanentemente.",
        responses={**common_errors}
    ),
)
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all().order_by('orden')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser] 

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicioCardSerializer
        return ServicioDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsGrupoAdministrador()]

@extend_schema_view(
    list=extend_schema(
        summary="Listar Categorías de Noticias",
        description="Devuelve la lista de categorías (ej: Agricultura, Eventos) para llenar el menú de filtros del frontend.",
        responses={200: CategoriaSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Categoría Individual",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Crear Categoría", 
        description="Solo Admin",
        responses={201: CategoriaSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Categoría", 
        description="Solo Admin",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Categoría", 
        description="Solo Admin",
        responses={**common_errors}
    ),
)
class CategoriaNoticiaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    lookup_field = 'slug'
    serializer_class = CategoriaSerializer

    def get_permissions(self):
        return [AllowAny()] if self.action in ['list', 'retrieve'] else [IsGrupoAdministrador()]

@extend_schema_view(
    list=extend_schema(
        summary="Listar Noticias (Cards)",
        description="Obtiene las noticias ordenadas por fecha. Soporta filtrado por categoría.",
        parameters=[
            OpenApiParameter(name='categoria', description='ID de la categoría para filtrar noticias', required=False, type=int),
            OpenApiParameter(name='es_destacada', description='Filtrar por true/false para mostrar solo destacadas', required=False, type=bool),
        ],
        responses={200: NoticiaCardSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Leer Noticia Completa",
        description="Trae el contenido completo, incluyendo el texto enriquecido (HTML) y el banner.",
        responses={200: NoticiaDetailSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Publicar Noticia", 
        description="Solo Admin. Recuerda enviar imagen_card e imagen_banner.", 
        responses={201: NoticiaDetailSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Noticia", 
        description="Solo Admin.", 
        responses={200: NoticiaDetailSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Noticia", 
        description="Solo Admin.", 
        responses={**common_errors}
    ),
)
class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all().order_by('-fecha_publicacion')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    filter_backends = [DjangoFilterBackend] 
    filterset_fields = ['categoria', 'es_destacada', 'publicado'] 

    def get_serializer_class(self):
        return NoticiaCardSerializer if self.action == 'list' else NoticiaDetailSerializer

    def get_permissions(self):
        return [AllowAny()] if self.action in ['list', 'retrieve'] else [IsGrupoAdministrador()]


@extend_schema_view(
    list=extend_schema(
        summary="Listar Categorías Investigación", 
        description="Para el menú de filtros.", 
        responses={200: CategoriaSerializer(many=True), **common_errors}
    ),
    create=extend_schema(
        summary="Crear Categoría Inv.", 
        description="Solo Admin",
        responses={201: CategoriaSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Categoría Inv.", 
        description="Solo Admin",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Categoría Inv.", 
        description="Solo Admin",
        responses={**common_errors}
    ),
)
class CategoriaInvestigacionViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsGrupoAdministrador()]


@extend_schema_view(
    list=extend_schema(
        summary="Listar Investigaciones (Cards)",
        description="Lista ligera. Filtra por ?categoria=ID o ?es_destacada=true",
        parameters=[
            OpenApiParameter(name='categoria', type=int, required=False),
            OpenApiParameter(name='es_destacada', type=bool, required=False),
        ],
        responses={200: InvestigacionCardSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Investigación Completa", 
        description="Incluye PDF y HTML.",
        responses={200: InvestigacionDetailSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Publicar Investigación", 
        description="Solo Admin. Soporta carga de archivos.",
        responses={201: InvestigacionDetailSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Investigación",
        responses={200: InvestigacionDetailSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Investigación",
        responses={**common_errors}
    ),
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
        return [IsGrupoAdministrador()]
    
@extend_schema_view(
    list=extend_schema(
        summary="Listar Certificaciones", 
        description="Muestra los logos y logros.",
        responses={200: CertificacionSerializer(many=True), **common_errors}
    ),
    create=extend_schema(
        summary="Crear Certificación", 
        description="Sube el logo y opcionalmente la URL de validación.",
        responses={201: CertificacionSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Certificación",
        responses={200: CertificacionSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Certificación",
        responses={**common_errors}
    ),
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
        return [IsGrupoAdministrador()]
    

@extend_schema_view(
    list=extend_schema(
        summary="Listar Testimonios", 
        description="Público: Ver aprobados. Admin: Ver todos.",
        responses={200: TestimonioSerializer(many=True), **common_errors}
    ),
    create=extend_schema(
        summary="Crear Testimonio", 
        description="Cualquier usuario autenticado.",
        responses={201: TestimonioSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Aprobar/Editar Testimonio", 
        description="Solo Admin. Puede cambiar es_visible a true.",
        responses={200: TestimonioAdminSerializer, **common_errors}
    ),
    partial_update=extend_schema(
        summary="Actualización Parcial Testimonio",
        responses={200: TestimonioAdminSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Testimonio", 
        description="Solo Admin.",
        responses={**common_errors}
    ),
)
class TestimonioViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonioSerializer
    
    # 1. PERMISOS:
    def get_permissions(self):
        # Crear: Cualquier usuario logueado (Cliente o Admin)
        if self.action == 'create':
            return [IsAuthenticatedOrReadOnly()]
        
        # Editar, Borrar, Actualizar Parcial: SOLO GRUPO ADMINISTRADOR
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsGrupoAdministrador()]
        
        # Listar y Ver Detalle: Público (Cualquiera)
        return [AllowAny()]

    # 2. QUERYSET INTELIGENTE (FILTRO POR GRUPO):
    def get_queryset(self):
        user = self.request.user
        
        # Verificamos si es del grupo Administrador
        es_admin = user.is_authenticated and (
            user.groups.filter(name='Administrador').exists() or user.is_superuser
        )

        # Si es Admin, ve TODOS (Pendientes y Aprobados) para poder moderar
        if es_admin:
            return Testimonio.objects.all().order_by('-created_at')
        
        # Si es Público/Cliente, solo ve los APROBADOS
        return Testimonio.objects.filter(es_visible=True).order_by('-created_at')

    # 3. SERIALIZADOR DINÁMICO:
    def get_serializer_class(self):
        user = self.request.user
        es_admin = user.is_authenticated and (
            user.groups.filter(name='Administrador').exists() or user.is_superuser
        )

        # Solo si es Admin y está editando, usamos el serializer que deja tocar 'es_visible'
        if es_admin:
            return TestimonioAdminSerializer
            
        # 3. Usuarios normales usan el serializer restringido
        return TestimonioSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

@extend_schema_view(
    list=extend_schema(
        summary="Listar Blog", 
        parameters=[OpenApiParameter(name='categoria', type=int)],
        responses={200: BlogCardSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Leer Artículo Completo",
        responses={200: BlogDetailSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Crear Post", 
        description="Solo Admin",
        responses={201: BlogDetailSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Post",
        responses={200: BlogDetailSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Post",
        responses={**common_errors}
    ),
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
        
        # CAMBIO: Validación por Grupo Administrador (Estandarizado)
        return [IsGrupoAdministrador()]

@extend_schema_view(
    list=extend_schema(
        summary="Listar Categorías Blog",
        responses={200: CategoriaSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Categoría Blog",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Crear Categoría Blog",
        responses={201: CategoriaSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Categoría Blog",
        responses={200: CategoriaSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Categoría Blog",
        responses={**common_errors}
    ),
)
class CategoriaBlogViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
             return [AllowAny()]
        # CAMBIO: Validación por Grupo Administrador
        return [IsGrupoAdministrador()]
    

@extend_schema_view(
    list=extend_schema(
        summary="Listar Protocolos (Grid)", 
        description="Devuelve la lista de cultivos para la rejilla principal.",
        responses={200: ProtocoloCardSerializer(many=True), **common_errors}
    ),
    retrieve=extend_schema(
        summary="Ver Detalle Protocolo (Modal)", 
        description="Devuelve la info técnica y el link del PDF.",
        responses={200: ProtocoloDetailSerializer, **common_errors}
    ),
    create=extend_schema(
        summary="Crear Protocolo", 
        description="Solo Admin. Requiere PDF.",
        responses={201: ProtocoloDetailSerializer, **common_errors}
    ),
    update=extend_schema(
        summary="Editar Protocolo", 
        description="Solo Admin.",
        responses={200: ProtocoloDetailSerializer, **common_errors}
    ),
    destroy=extend_schema(
        summary="Eliminar Protocolo", 
        description="Solo Admin.",
        responses={**common_errors}
    ),
)
class ProtocoloViewSet(viewsets.ModelViewSet):
    # Por defecto mostramos solo los visibles, pero el get_queryset tiene la última palabra
    queryset = Protocolo.objects.filter(es_visible=True).order_by('orden')
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['titulo', 'contenido'] 

    def get_queryset(self):
        user = self.request.user
        
        # Validamos si es del grupo 'Administrador' o Superusuario
        es_admin = user.is_authenticated and (
            user.groups.filter(name='Administrador').exists() or user.is_superuser
        )

        # Si es Admin, ve TODO (incluyendo ocultos)
        if es_admin:
            return Protocolo.objects.all().order_by('orden')
            
        # Si es Público, solo visibles
        return Protocolo.objects.filter(es_visible=True).order_by('orden')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProtocoloCardSerializer
        return ProtocoloDetailSerializer

    def get_permissions(self):
        # Lectura pública
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
            
        # Escritura (Crear, Editar, Borrar): Solo Grupo Administrador
        return [IsGrupoAdministrador()]