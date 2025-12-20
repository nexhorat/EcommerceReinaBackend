import sys
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

class WebPConverterMixin:
    """
    Mixin para convertir automáticamente campos de imagen a WebP antes de guardar.
    """
    
    def convertir_imagen_a_webp(self, field_name):
        # 1. Obtener el campo de imagen dinámicamente usando el nombre (string)
        imagen_field = getattr(self, field_name)

        # Si no hay imagen, no hacemos nada
        if not imagen_field:
            return

        try:
            # Abrimos la imagen
            img = Image.open(imagen_field)
        except Exception:
            return 

        # Si ya es WebP, detenemos para no re-procesar
        if img.format == 'WEBP':
            return

        # 2. Procesamiento de imagen
        output_io = BytesIO()
        
        # Convertir modos no compatibles (como transparencia indexada) a RGBA
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        # 3. Guardar comprimida en memoria
        img.save(output_io, format='WEBP', quality=85)
        output_io.seek(0)

        # 4. Generar nuevo nombre reemplazando la extensión
        nombre_actual = imagen_field.name
        # Esto maneja casos donde el nombre ya tenga ruta 'carpeta/foto.jpg'
        nombre_base = nombre_actual.rsplit('.', 1)[0] 
        nuevo_nombre = f"{nombre_base}.webp"

        # 5. Asignar el nuevo archivo al campo
        archivo_nuevo = InMemoryUploadedFile(
            output_io,
            'ImageField',
            nuevo_nombre,
            'image/webp',
            sys.getsizeof(output_io),
            None
        )
        
        # Seteamos el atributo en el modelo con el nuevo archivo
        setattr(self, field_name, archivo_nuevo)