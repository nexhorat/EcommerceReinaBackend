from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Pedido, Producto # Modelo que crearemos en el punto 4

@receiver(post_save, sender=Pedido)
def enviar_correo_confirmacion(sender, instance, created, **kwargs):
    if created:
        asunto = f"Confirmación de Pedido #{instance.id}"
        mensaje = f"Hola {instance.usuario.first_name}, hemos recibido tu pedido por un total de ${instance.total}."
        destinatario = [instance.usuario.email]
        
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            destinatario,
            fail_silently=False,
        )


@receiver(post_save, sender=Producto)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    if created:
        # Lógica de envío de correo similar a la de marketing
        pass