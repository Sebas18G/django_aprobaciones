import uuid
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from .constants import MENSAJES

#utils.py

def generar_id_solicitud():
    """Genera un ID único para la solicitud"""
    return str(uuid.uuid4())

def obtener_timestamp():
    """Obtiene timestamp actual formateado"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def enviar_notificacion_email(destinatario, asunto, mensaje, solicitud_data=None):
    """
    Envía notificación por email (simulado por ahora)
    En producción, aquí implementaríamos el envío real
    """
    try:
        # Por ahora solo logeamos la notificación
        print(f"[NOTIFICACIÓN EMAIL]")
        print(f"Para: {destinatario}")
        print(f"Asunto: {asunto}")
        print(f"Mensaje: {mensaje}")
        if solicitud_data:
            print(f"Datos de solicitud: {solicitud_data}")
        print("-" * 50)
        
        # En producción, descomenta esto:
        # send_mail(
        #     asunto,
        #     mensaje,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [destinatario],
        #     fail_silently=False,
        # )
        
        return True
    except Exception as e:
        print(f"Error enviando notificación: {e}")
        return False

def validar_usuario_red(usuario):
    """
    Valida formato de usuario de red
    Por ahora validación básica, en producción conectar con AD/LDAP
    """
    if not usuario:
        return False, "Usuario no puede estar vacío"
    
    if len(usuario) < 3:
        return False, "Usuario debe tener al menos 3 caracteres"
    
    # Validaciones adicionales según estándar de la empresa
    if not usuario.isalnum():
        return False, "Usuario solo puede contener letras y números"
    
    return True, "Usuario válido"

def formatear_tipo_solicitud(tipo):
    """Convierte el código de tipo en texto legible"""
    tipos_dict = dict(TIPOS_SOLICITUD)
    return tipos_dict.get(tipo, tipo.title())

def obtener_color_estado(estado):
    """Devuelve el color CSS para un estado dado"""
    colores = {
        'pendiente': 'warning',
        'en_revision': 'info',
        'aprobado': 'success',
        'rechazado': 'danger',
        'cancelado': 'secondary'
    }
    return colores.get(estado, 'secondary')

def crear_mensaje_notificacion(tipo_accion, solicitud_data):
    """Crea el mensaje de notificación basado en la acción"""
    mensajes = {
        'nueva_solicitud': f"""
        Nueva solicitud de aprobación recibida:
        
        ID: {solicitud_data.get('id', 'N/A')}
        Título: {solicitud_data.get('titulo', 'N/A')}
        Solicitante: {solicitud_data.get('solicitante', 'N/A')}
        Tipo: {formatear_tipo_solicitud(solicitud_data.get('tipo_solicitud', 'N/A'))}
        
        Por favor, revisa y procesa esta solicitud.
        """,
        
        'solicitud_aprobada': f"""
        Tu solicitud ha sido aprobada:
        
        ID: {solicitud_data.get('id', 'N/A')}
        Título: {solicitud_data.get('titulo', 'N/A')}
        Aprobada por: {solicitud_data.get('aprobador', 'N/A')}
        
        Puedes proceder con la implementación.
        """,
        
        'solicitud_rechazada': f"""
        Tu solicitud ha sido rechazada:
        
        ID: {solicitud_data.get('id', 'N/A')}
        Título: {solicitud_data.get('titulo', 'N/A')}
        Rechazada por: {solicitud_data.get('aprobador', 'N/A')}
        Comentario: {solicitud_data.get('comentario', 'Sin comentarios')}
        
        Puedes crear una nueva solicitud con las correcciones necesarias.
        """
    }
    
    return mensajes.get(tipo_accion, "Actualización en tu solicitud")

# Importar las constantes para que estén disponibles
from .constants import ESTADOS_SOLICITUD, TIPOS_SOLICITUD, PRIORIDADES