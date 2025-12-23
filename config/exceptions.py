from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado que asegura una estructura JSON estándar
    para todos los errores, y documenta automáticamente en logs los errores 500.
    """
    # Llama al manejador por defecto de DRF primero
    response = exception_handler(exc, context)

    # Si DRF no manejó la excepción (ej. error de servidor 500 estándar de Python)
    if response is None:
        if isinstance(exc, Http404):
            response = Response(
                {"detail": "Recurso no encontrado.", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, PermissionDenied):
            response = Response(
                {"detail": "No tienes permiso para realizar esta acción.", "code": "permission_denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            # Aquí capturamos errores inesperados (500)
            # REGISTRAR EL ERROR REAL EN LOGS (Crítico para seguridad/debugging)
            logger.error(f"Error inesperado en {context['view'].__class__.__name__}: {exc}", exc_info=True)
            
            response = Response(
                {
                    "detail": "Ocurrió un error interno en el servidor.",
                    "code": "internal_server_error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Estandarizar la estructura de respuesta de DRF
    # DRF a veces devuelve listas o diccionarios directos. Vamos a envolverlos.
    if response is not None:
        if not isinstance(response.data, dict) or 'detail' not in response.data:
            # Si son errores de validación de campos (dict de errores)
            response.data = {
                "detail": "Error de validación de datos.",
                "code": "validation_error",
                "errors": response.data
            }
        else:
            # Si ya tiene 'detail', aseguramos que tenga un 'code' si falta
            if 'code' not in response.data:
                response.data['code'] = response.status_code

    return response