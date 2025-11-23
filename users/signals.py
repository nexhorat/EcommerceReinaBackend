from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_default_group(sender, instance, created, **kwargs):
    """
    Se ejecuta cada vez que se crea un usuario nuevo.
    """
    if created:
        group, _ = Group.objects.get_or_create(name='Usuario')
        
        if instance.is_superuser:
            admin_group, _ = Group.objects.get_or_create(name='Administrador')
            instance.groups.add(admin_group)
        else:
            instance.groups.add(group)