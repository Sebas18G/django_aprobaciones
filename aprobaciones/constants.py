# constants.py - Constantes para el sistema de aprobaciones

# Estados posibles de las solicitudes
ESTADOS_SOLICITUD = [
    ('pendiente', 'Pendiente'),
    ('en_revision', 'En Revisión'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
    ('cancelado', 'Cancelado'),
]

# Tipos de solicitudes
TIPOS_SOLICITUD = [
    ('despliegue', 'Despliegue a Producción'),
    ('acceso', 'Solicitud de Acceso'),
    ('cambio_tecnico', 'Cambio Técnico'),
    ('pipeline', 'Configuración Pipeline'),
    ('incorporacion', 'Incorporación Personal'),
    ('otro', 'Otro'),
]

# Prioridades de las solicitudes
PRIORIDADES = [
    ('baja', 'Baja'),
    ('media', 'Media'),
    ('alta', 'Alta'),
    ('critica', 'Crítica'),
]

# Mensajes del sistema
MENSAJES = {
    'solicitud_creada': 'La solicitud ha sido creada exitosamente.',
    'solicitud_aprobada': 'La solicitud ha sido aprobada.',
    'solicitud_rechazada': 'La solicitud ha sido rechazada.',
    'solicitud_no_encontrada': 'La solicitud solicitada no fue encontrada.',
    'error_permisos': 'No tienes permisos para realizar esta acción.',
    'error_estado_invalido': 'El estado especificado no es válido.',
    'error_actualizacion': 'Error al actualizar la solicitud.',
}

# Colores para estados (Bootstrap classes)
COLORES_ESTADO = {
    'pendiente': 'warning',
    'en_revision': 'info',
    'aprobado': 'success',
    'rechazado': 'danger',
    'cancelado': 'secondary',
}

# Iconos para estados (Font Awesome)
ICONOS_ESTADO = {
    'pendiente': 'fas fa-hourglass-half',
    'en_revision': 'fas fa-eye',
    'aprobado': 'fas fa-check-circle',
    'rechazado': 'fas fa-times-circle',
    'cancelado': 'fas fa-ban',
}

# Estados que permiten modificación
ESTADOS_MODIFICABLES = ['pendiente', 'en_revision']

# Estados finales (no permiten cambios posteriores)
ESTADOS_FINALES = ['aprobado', 'rechazado', 'cancelado']

# Acciones válidas en el historial
ACCIONES_HISTORIAL = [
    ('creada', 'Creada'),
    ('actualizada', 'Actualizada'),
    ('aprobado', 'Aprobada'),
    ('rechazado', 'Rechazada'),
    ('cancelado', 'Cancelada'),
    ('en_revision', 'En Revisión'),
]

# Tipos de comentarios
TIPOS_COMENTARIO = [
    ('general', 'Comentario General'),
    ('aprobado', 'Comentario de Aprobación'),
    ('rechazado', 'Comentario de Rechazo'),
    ('revision', 'Comentario de Revisión'),
]