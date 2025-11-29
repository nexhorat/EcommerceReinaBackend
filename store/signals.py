from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Pedido, Producto

User = get_user_model()

@receiver(post_save, sender=Pedido)
def enviar_correo_confirmacion(sender, instance, created, **kwargs):
    if created:
        asunto = f"Confirmación de Pedido #{instance.id} - Ecommerce Reina"
        mensaje = f"Hola {instance.usuario.first_name}, hemos recibido tu pedido por un total de ${instance.total}.\n\nTu pedido está en estado: {instance.get_estado_display()}."
        destinatario = [instance.usuario.email]
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                destinatario,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando correo pedido: {e}")

@receiver(post_save, sender=Producto)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    """
    Envía un correo a TODOS los usuarios cuando se crea un producto nuevo.
    """
    if created and instance.stock > 0: # Solo si hay stock inicial
        # Obtener todos los correos (¡Cuidado en producción con listas grandes! Usar Celery idealmente)
        destinatarios = list(User.objects.values_list('email', flat=True))
        
        asunto = f"¡Nuevo Lanzamiento! {instance.nombre}"
        mensaje = f"Descubre nuestro nuevo producto: {instance.nombre}.\n\n{instance.descripcion[:100]}...\n\nPrecio: ${instance.precio}"

        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando notificación masiva producto: {e}")