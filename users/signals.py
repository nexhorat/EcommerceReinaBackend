from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_created_actions(sender, instance, created, **kwargs):
    """
    Maneja acciones post-creación de usuario: Asignar grupo y Enviar correo.
    """
    if created:
        # 1. Asignar Grupo por defecto (Lógica existente)
        group, _ = Group.objects.get_or_create(name='Usuario')
        if instance.is_superuser:
            admin_group, _ = Group.objects.get_or_create(name='Administrador')
            instance.groups.add(admin_group)
        else:
            instance.groups.add(group)

        # 2. Enviar Correo de Bienvenida (Nueva funcionalidad)
        try:
            send_mail(
                subject='¡Bienvenido a Ecommerce Reina!',
                message=f'Hola {instance.first_name}, gracias por registrarte en nuestra plataforma.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True, # Para que no rompa el registro si falla el correo
            )
        except Exception as e:
            print(f"Error enviando correo de bienvenida: {e}")