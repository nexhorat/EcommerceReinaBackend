# store/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Producto, Pedido

User = get_user_model()

# --- 1. Notificación de Nuevo Producto ---
@receiver(post_save, sender=Producto)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    if created: # Solo al crear
        # Filtrar usuarios interesados en ofertas
        destinatarios = User.objects.filter(is_active=True, recibir_ofertas=True).values_list('email', flat=True)
        
        if not destinatarios:
            return

        link = f"http://localhost:3000/tienda/{instance.slug}"
        imagen_url = f"http://127.0.0.1:8000{instance.imagen_principal.url}" if instance.imagen_principal else ""

        html_content = render_to_string('emails/nuevo_contenido.html', {
            'titulo': "¡Nuevo Producto Disponible!",
            'tipo_contenido': "NUEVO LANZAMIENTO",
            'titulo_contenido': instance.nombre,
            'resumen': instance.descripcion[:200] + "...", # Recortar descripción
            'link': link,
            'imagen_url': imagen_url
        })
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            f"🎁 Nuevo Producto: {instance.nombre}",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            bcc=list(destinatarios)
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


# --- 2. Notificación de Pedido (Compra) ---
@receiver(post_save, sender=Pedido)
def notificar_pedido(sender, instance, created, **kwargs):
    """
    Se ejecuta al crear el pedido o al cambiar su estado.
    Enviaremos correo solo cuando se cree (Confirmación de recibido).
    """
    if created:
        # A. Correo al CLIENTE
        try:
            items = instance.detalles.all() # Relación reverse de DetallePedido
            
            # Dirección string
            dir_str = str(instance.direccion_envio) if instance.direccion_envio else "Sin dirección"

            html_user = render_to_string('emails/confirmacion_pedido.html', {
                'nombre': instance.usuario.first_name,
                'pedido_id': instance.id,
                'items': items,
                'total': instance.total,
                'direccion': dir_str
            })
            text_user = strip_tags(html_user)

            msg_user = EmailMultiAlternatives(
                f"Confirmación de Pedido #{instance.id}",
                text_user,
                settings.DEFAULT_FROM_EMAIL,
                [instance.usuario.email]
            )
            msg_user.attach_alternative(html_user, "text/html")
            msg_user.send()

        except Exception as e:
            print(f"Error enviando confirmación de pedido al cliente: {e}")

        # B. Correo de Alerta al ADMIN (Como notificación web)
        try:
            # Lista de correos de administradores
            admins = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            
            if admins:
                send_mail(
                    subject=f"🔔 Nueva Venta: Pedido #{instance.id}",
                    message=f"El usuario {instance.usuario.email} ha realizado una compra por ${instance.total}. Revisa el panel de administración.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(admins),
                    fail_silently=True
                )
        except Exception as e:
            print(f"Error notificando al admin: {e}")