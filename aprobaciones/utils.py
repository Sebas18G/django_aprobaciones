import uuid
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from .constants import (
    MENSAJES, TIPOS_SOLICITUD, COLORES_ESTADO, 
    ICONOS_ESTADO, ESTADOS_SOLICITUD
)

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
    if not usuario.replace('.', '').replace('_', '').isalnum():
        return False, "Usuario solo puede contener letras, números, puntos y guiones bajos"
    
    return True, "Usuario válido"

def formatear_tipo_solicitud(tipo):
    """Convierte el código de tipo en texto legible"""
    tipos_dict = dict(TIPOS_SOLICITUD)
    return tipos_dict.get(tipo, tipo.replace('_', ' ').title())

def obtener_color_estado(estado):
    """Devuelve el color CSS para un estado dado"""
    return COLORES_ESTADO.get(estado, 'secondary')

def obtener_icono_estado(estado):
    """Devuelve el icono CSS para un estado dado"""
    return ICONOS_ESTADO.get(estado, 'fas fa-question-circle')

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

Puedes proceder con la implementación.
        """,
        
        'solicitud_rechazada': f"""
Tu solicitud ha sido rechazada:

ID: {solicitud_data.get('id', 'N/A')}
Título: {solicitud_data.get('titulo', 'N/A')}

Por favor, revisa los comentarios y crea una nueva solicitud con las correcciones necesarias.
        """
    }
    
    return mensajes.get(tipo_accion, "Actualización en tu solicitud")

def validar_cambio_estado(estado_actual, estado_nuevo):
    """Valida si un cambio de estado es permitido"""
    from .constants import ESTADOS_FINALES, ESTADOS_MODIFICABLES
    
    # No se puede cambiar desde estados finales
    if estado_actual in ESTADOS_FINALES:
        return False, f"No se puede cambiar el estado desde '{estado_actual}'"
    
    # Validar que el nuevo estado existe
    estados_validos = [estado[0] for estado in ESTADOS_SOLICITUD]
    if estado_nuevo not in estados_validos:
        return False, f"Estado '{estado_nuevo}' no es válido"
    
    # Reglas específicas de negocio
    transiciones_validas = {
        'pendiente': ['en_revision', 'aprobado', 'rechazado', 'cancelado'],
        'en_revision': ['aprobado', 'rechazado', 'pendiente', 'cancelado'],
    }
    
    if estado_actual in transiciones_validas:
        if estado_nuevo not in transiciones_validas[estado_actual]:
            return False, f"No se puede cambiar de '{estado_actual}' a '{estado_nuevo}'"
    
    return True, "Cambio de estado válido"

def formatear_fecha_local(fecha_iso):
    """Convierte fecha ISO a formato local"""
    try:
        if isinstance(fecha_iso, str):
            fecha = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        else:
            fecha = fecha_iso
        return fecha.strftime('%d/%m/%Y %H:%M')
    except:
        return 'Fecha no disponible'

def generar_codigo_solicitud(tipo_solicitud):
    """Genera un código legible para la solicitud"""
    prefijos = {
        'despliegue': 'DEPL',
        'acceso': 'ACC',
        'cambio_tecnico': 'TECH',
        'pipeline': 'PIPE',
        'incorporacion': 'INC',
        'otro': 'OTR'
    }
    
    prefijo = prefijos.get(tipo_solicitud, 'SOL')
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    return f"{prefijo}-{timestamp}"

def limpiar_descripcion(descripcion):
    """Limpia y formatea la descripción de la solicitud"""
    if not descripcion:
        return ""
    
    # Eliminar espacios extra y saltos de línea innecesarios
    descripcion = descripcion.strip()
    descripcion = ' '.join(descripcion.split())
    
    return descripcion

def obtener_mensaje_sistema(clave, **kwargs):
    """Obtiene un mensaje del sistema con formato"""
    mensaje = MENSAJES.get(clave, f"Mensaje no encontrado: {clave}")
    if kwargs:
        try:
            mensaje = mensaje.format(**kwargs)
        except KeyError as e:
            print(f"Error formateando mensaje {clave}: {e}")
    
    return mensaje