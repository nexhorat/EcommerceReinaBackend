# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager 

class User(AbstractUser):
    username = None 
    email = models.EmailField('Dirección de correo', unique=True)
    
    # Hacemos obligatorios el nombre y apellido
    first_name = models.CharField('Nombres', max_length=150)
    last_name = models.CharField('Apellidos', max_length=150)
    
    # Otros campos personalizados
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/', 
        blank=True, 
        null=True, 
        verbose_name="Foto de Perfil"
    )

    # Configuraciones de autenticación
    USERNAME_FIELD = 'email' # El login será con email
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Campos obligatorios al crear superuser por consola

    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"