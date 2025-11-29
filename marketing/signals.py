# marketing/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Noticia, Blog, Protocolo, Investigacion, Servicio

User = get_user_model()

def enviar_notificacion_masiva(titulo, tipo_contenido, slug):
    """
    Función auxiliar para enviar correos.
    ADVERTENCIA: En producción, esto debe hacerse con tareas asíncronas (Celery).
    Hacerlo así puede poner lento el guardado si hay muchos usuarios.
    """
    # Obtenemos todos los emails de los usuarios
    destinatarios = list(User.objects.values_list('email', flat=True))
    
    asunto = f"Nuevo contenido publicado: {tipo_contenido}"
    mensaje = f"Hola, hemos publicado un nuevo {tipo_contenido}: '{titulo}'.\n\nVisítalo en nuestra web."

    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios, 
            fail_silently=True
        )
    except Exception as e:
        print(f"Error enviando notificación masiva: {e}")

@receiver(post_save, sender=Noticia)
def notificar_nueva_noticia(sender, instance, created, **kwargs):
    if created and instance.publicado:
        enviar_notificacion_masiva(instance.titulo, "Noticia", instance.slug)

@receiver(post_save, sender=Blog)
def notificar_nuevo_blog(sender, instance, created, **kwargs):
    if created and instance.publicado:
        enviar_notificacion_masiva(instance.titulo, "Artículo de Blog", instance.slug)

@receiver(post_save, sender=Investigacion)
def notificar_nueva_investigacion(sender, instance, created, **kwargs):
    if created and instance.publicado:
        enviar_notificacion_masiva(instance.titulo, "Investigación", instance.slug)

@receiver(post_save, sender=Protocolo)
def notificar_nuevo_protocolo(sender, instance, created, **kwargs):
    if created and instance.es_visible:
        enviar_notificacion_masiva(instance.titulo, "Protocolo de Cultivo", instance.slug)