from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User

@receiver(post_migrate)
def create_initial_roles(sender, **kwargs):
    """
    Se ejecuta automáticamente después de correr 'python manage.py migrate'.
    Garantiza que los grupos y permisos existan en la base de datos.
    """
    # Evitamos que se ejecute múltiples veces, solo cuando la app 'users' (o la que definas) termine
    # Nota: Si los permisos de 'store' no existen aún, se capturará la excepción y se intentará en la siguiente migración.
    if sender.name != 'users':
        return

    print("--- Configurando roles y permisos iniciales ---")

    # 1. Crear Grupos Base
    # Usamos get_or_create para que sea idempotente (no falle si ya existen)
    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    usuario_group, _ = Group.objects.get_or_create(name='Usuario')
    despachador_group, _ = Group.objects.get_or_create(name='Despachador')

    # 2. Asignar Permisos al Despachador
    # Intentamos obtener el modelo Pedido de forma segura
    try:
        Pedido = apps.get_model('store', 'Pedido')
        pedido_content_type = ContentType.objects.get_for_model(Pedido)

        # Buscamos los permisos específicos: Ver y Cambiar (editar) Pedido
        # permisos_despachador = Permission.objects.filter(
        #     content_type=pedido_content_type,
        #     codename__in=['view_pedido', 'change_pedido']
        # )

        # Asignamos los permisos al grupo
        # if permisos_despachador.exists():
        #    despachador_group.permissions.set(permisos_despachador)
        #    print("✅ Rol 'Despachador' configurado con permisos de Pedido.")
        #else:
        #    print("⚠️ Los permisos de Pedido aún no están disponibles en la DB.")

    except LookupError:
        # Esto ocurre si la app 'store' no está instalada o cargada aún
        print("⚠️ La app 'store' no está lista, se omitió la asignación de permisos al Despachador.")
    except Exception as e:
        print(f"⚠️ Error configurando permisos: {e}")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_created_actions(sender, instance, created, **kwargs):
    """
    Maneja acciones post-creación de usuario: Asignar grupo y Enviar correo.
    """
    if created:
        # 1. Asignar Grupo por defecto
        # Si es superusuario, le damos admin
        if instance.is_superuser:
            admin_group, _ = Group.objects.get_or_create(name='Administrador')
            instance.groups.add(admin_group)
        else:
            # Si es usuario normal, le asignamos 'Cliente' (antes 'Usuario')
            cliente_group, _ = Group.objects.get_or_create(name='Usuario')
            instance.groups.add(cliente_group)

        # 2. Enviar Correo de Bienvenida
        try:
            subject = '¡Bienvenido a la Familia Reina!'
            
            # Renderizamos el HTML con los datos del usuario
            html_content = render_to_string('emails/bienvenida.html', {
                'nombre': instance.first_name or instance.email
            })
            
            # Versión texto plano por si el correo del cliente no soporta HTML
            text_content = strip_tags(html_content)

            # Preparamos el mensaje
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
        except Exception as e:
            print(f"Error enviando correo de bienvenida: {e}")