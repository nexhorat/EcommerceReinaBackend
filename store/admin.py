from django.contrib import admin
from .models import Producto, Pedido, DetallePedido, Favorito, TarifaEnvio, Direccion

# --- 1. Configuración de Tarifas de Envío ---
@admin.register(TarifaEnvio)
class TarifaEnvioAdmin(admin.ModelAdmin):
    list_display = ('ciudad', 'departamento', 'precio_base', 'precio_extra_producto')
    list_filter = ('departamento',)
    search_fields = ('ciudad', 'departamento')
    ordering = ('ciudad',)
    help_text = "Configura aquí los precios de envío por ciudad."

# --- 2. Gestión de Direcciones (Soporte) ---
@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ciudad', 'direccion', 'telefono', 'es_principal')
    list_filter = ('ciudad', 'es_principal')
    search_fields = ('usuario__email', 'usuario__first_name', 'direccion', 'ciudad')
    autocomplete_fields = ['usuario'] # Requiere que UserAdmin tenga search_fields configurado

# --- 3. Productos (Sin cambios mayores) ---
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'es_destacado')
    list_filter = ('categoria', 'es_destacado')
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    autocomplete_fields = ['relacionados']

# --- 4. Pedidos (Actualizado con Envío) ---
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    readonly_fields = ('precio_unitario',) 
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Agregamos 'ciudad_destino' y 'total' para ver rápido la info clave
    list_display = ('id', 'usuario', 'ciudad_destino', 'estado', 'total', 'created_at')
    
    # Filtros útiles para logística
    list_filter = ('estado', 'created_at', 'direccion_envio__ciudad')
    
    # Buscador por usuario o ID de pedido
    search_fields = ('id', 'usuario__email', 'usuario__first_name')
    
    inlines = [DetallePedidoInline]
    
    # Campos que no se deben editar manualmente para evitar descuadres contables
    readonly_fields = ('usuario', 'subtotal', 'costo_envio', 'total', 'created_at', 'transaccion_id', 'metodo_pago')

    # Agrupamos los campos en secciones para orden visual
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'estado', 'created_at')
        }),
        ('Datos de Envío', {
            'fields': ('direccion_envio', 'costo_envio')
        }),
        ('Datos de Pago', {
            'fields': ('subtotal', 'total', 'metodo_pago', 'transaccion_id')
        }),
    )

    # Método para mostrar la ciudad en la lista principal (list_display)
    def ciudad_destino(self, obj):
        if obj.direccion_envio:
            return f"{obj.direccion_envio.ciudad} ({obj.direccion_envio.departamento})"
        return "Sin dirección"
    ciudad_destino.short_description = "Destino"

admin.site.register(Favorito)