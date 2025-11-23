from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    
    # Importante: redefinir fieldsets para quitar referencias a 'username'
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'telefono')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password'),
        }),
    )

admin.site.register(User, CustomUserAdmin)