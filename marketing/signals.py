# marketing/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

# Importamos todos los modelos que generan notificación
from .models import Noticia, Blog, Investigacion, Protocolo, Testimonio

User = get_user_model()

def enviar_notificacion_masiva(instance, tipo_contenido, titulo, resumen, imagen=None):
    """
    Función auxiliar para enviar correos a todos los suscritos.
    """
    # 1. Filtrar usuarios suscritos y activos
    destinatarios = User.objects.filter(is_active=True, recibir_newsletter=True).values_list('email', flat=True)
    
    if not destinatarios:
        return

    # 2. Preparar el contenido HTML
    # URL ficticia al frontend, ajusta según tu routing de React/Angular
    link_frontend = f"http://urlficticafrontend:3000/{tipo_contenido.lower()}s/{instance.slug}"
    
    imagen_url = ""
    if imagen:
        # Aseguramos que la URL sea absoluta si usas almacenamiento local
        # En producción con S3 esto cambia, pero para local sirve:
        imagen_url = f"http://127.0.0.1:8000{imagen.url}"

    html_content = render_to_string('emails/nuevo_contenido.html', {
        'titulo': f"Nueva Publicación: {titulo}",
        'tipo_contenido': tipo_contenido,
        'titulo_contenido': titulo,
        'resumen': resumen,
        'link': link_frontend,
        'imagen_url': imagen_url
    })
    text_content = strip_tags(html_content)

    # 3. Enviar correos en bloque (Mass Mail)
    # Usamos una sola conexión para ser eficientes
    connection = get_connection()
    messages = []
    
    subject = f"📢 Nuevo en Ecommerce Reina: {titulo}"
    
    # Nota: Para listas grandes, esto debe ir a una tarea asíncrona (Celery)
    # Aquí lo hacemos simple usando CCO (BCC) para no revelar correos entre sí,
    # o enviando uno por uno si necesitamos personalizar el nombre.
    # Por eficiencia y privacidad básica, usaremos BCC en un solo correo o lotes.
    
    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, 
        bcc=list(destinatarios), # BCC oculta los destinatarios entre sí
        connection=connection
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@receiver(post_save, sender=Noticia)
@receiver(post_save, sender=Blog)
@receiver(post_save, sender=Investigacion)
@receiver(post_save, sender=Protocolo)
def notificar_nuevo_contenido(sender, instance, created, **kwargs):
    # Solo notificar si se acaba de crear y está publicado
    # Opcional: Podrías añadir lógica para detectar si cambió de borrador a publicado
    if created and instance.publicado:
        
        # Determinar tipo para el correo
        tipo = sender.__name__ # "Noticia", "Blog", etc.
        
        # Unificar campos (algunos modelos tienen imagen_card, otros descripcion_tecnica, etc)
        resumen = getattr(instance, 'resumen', getattr(instance, 'descripcion_tecnica', ''))
        imagen = getattr(instance, 'imagen_card', None)
        
        enviar_notificacion_masiva(
            instance=instance,
            tipo_contenido=tipo,
            titulo=instance.titulo,
            resumen=resumen,
            imagen=imagen
        )

@receiver(post_save, sender=Testimonio)
def notificar_nuevo_testimonio(sender, instance, created, **kwargs):
    if created:
        # 1. Obtener admins
        admins = User.objects.filter(
            groups__name='Administrador', 
            is_active=True
        ).values_list('email', flat=True)

        if not admins:
            admins = User.objects.filter(is_superuser=True).values_list('email', flat=True)
            
        if not admins:
            return

        # 2. Generar Link directo al panel de administración de Django
        # Asumiendo que corres en local puerto 8000. En producción cambia esto por tu dominio.
        link_admin = f"http://127.0.0.1:8000/admin/marketing/testimonio/{instance.id}/change/"

        # 3. Renderizar HTML
        html_content = render_to_string('emails/admin_nuevo_testimonio.html', {
            'usuario': instance.usuario.get_full_name() or instance.usuario.email,
            'contenido': instance.contenido,
            'cargo': instance.cargo_empresa or "No especificado",
            'link_admin': link_admin
        })
        text_content = strip_tags(html_content)

        # 4. Enviar correo
        msg = EmailMultiAlternatives(
            f"💬 Nuevo Comentario Pendiente de {instance.usuario.first_name}",
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            to=list(admins) # Enviamos a todos los admins
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()