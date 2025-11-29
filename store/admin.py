from django.contrib import admin
from .models import Producto, Pedido, DetallePedido, Favorito

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'es_destacado')
    list_filter = ('categoria', 'es_destacado')
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    autocomplete_fields = ['relacionados'] # Útil si hay muchos productos

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    readonly_fields = ('precio_unitario',) # Para mantener histórico
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'estado', 'created_at')
    list_filter = ('estado', 'created_at')
    inlines = [DetallePedidoInline]
    readonly_fields = ('total', 'usuario')

admin.site.register(Favorito)