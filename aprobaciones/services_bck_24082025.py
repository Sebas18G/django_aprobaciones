import json
import os
from datetime import datetime
from django.conf import settings
from .utils import generar_id_solicitud, enviar_notificacion_email, crear_mensaje_notificacion

#services.py

class SolicitudStorageService:
    """
    Servicio temporal para almacenar solicitudes en archivo JSON
    En producción esto será reemplazado por modelos Django y base de datos
    """
    
    def __init__(self):
        # Crear directorio de datos si no existe
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.file_path = os.path.join(self.data_dir, 'solicitudes.json')
    
    def _load_data(self):
        """Cargar datos del archivo JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_data(self, data):
        """Guardar datos al archivo JSON"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def crear_solicitud(self, form_data):
        """Crear una nueva solicitud"""
        solicitudes = self._load_data()
        
        # Crear nueva solicitud
        nueva_solicitud = {
            'id': generar_id_solicitud(),
            'titulo': form_data['titulo'],
            'descripcion': form_data['descripcion'],
            'solicitante': form_data['solicitante'],
            'responsable': form_data['responsable'],
            'tipo_solicitud': form_data['tipo_solicitud'],
            'estado': 'pendiente',
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_actualizacion': datetime.now().isoformat(),
            'historial': [
                {
                    'accion': 'creada',
                    'usuario': form_data['solicitante'],
                    'fecha': datetime.now().isoformat(),
                    'comentario': 'Solicitud creada'
                }
            ],
            'comentarios': []
        }
        
        # Agregar a la lista
        solicitudes.append(nueva_solicitud)
        
        # Guardar
        self._save_data(solicitudes)
        
        # Enviar notificación al responsable
        self._enviar_notificacion_nueva_solicitud(nueva_solicitud)
        
        return nueva_solicitud
    
    def obtener_todas_solicitudes(self):
        """Obtener todas las solicitudes"""
        return self._load_data()
    
    def obtener_solicitud_por_id(self, solicitud_id):
        """Obtener una solicitud específica por ID"""
        solicitudes = self._load_data()
        for solicitud in solicitudes:
            if solicitud['id'] == solicitud_id:
                return solicitud
        return None
    
    def actualizar_solicitud(self, solicitud_id, nuevos_datos):
        """Actualizar una solicitud existente"""
        solicitudes = self._load_data()
        
        for i, solicitud in enumerate(solicitudes):
            if solicitud['id'] == solicitud_id:
                # Actualizar campos
                for key, value in nuevos_datos.items():
                    if key != 'id':  # No permitir cambiar el ID
                        solicitud[key] = value
                
                solicitud['fecha_actualizacion'] = datetime.now().isoformat()
                solicitudes[i] = solicitud
                
                self._save_data(solicitudes)
                return solicitud
        
        return None
    
    def aprobar_solicitud(self, solicitud_id, aprobador, comentario=''):
        """Aprobar una solicitud"""
        return self._cambiar_estado_solicitud(solicitud_id, 'aprobado', aprobador, comentario)
    
    def rechazar_solicitud(self, solicitud_id, aprobador, comentario=''):
        """Rechazar una solicitud"""
        return self._cambiar_estado_solicitud(solicitud_id, 'rechazado', aprobador, comentario)
    
    def _cambiar_estado_solicitud(self, solicitud_id, nuevo_estado, usuario, comentario=''):
        """Cambiar el estado de una solicitud"""
        solicitudes = self._load_data()
        
        for i, solicitud in enumerate(solicitudes):
            if solicitud['id'] == solicitud_id:
                estado_anterior = solicitud['estado']
                solicitud['estado'] = nuevo_estado
                solicitud['fecha_actualizacion'] = datetime.now().isoformat()
                
                # Agregar al historial
                entrada_historial = {
                    'accion': nuevo_estado,
                    'usuario': usuario,
                    'fecha': datetime.now().isoformat(),
                    'comentario': comentario or f'Solicitud {nuevo_estado}',
                    'estado_anterior': estado_anterior
                }
                solicitud['historial'].append(entrada_historial)
                
                # Agregar comentario si existe
                if comentario:
                    solicitud['comentarios'].append({
                        'usuario': usuario,
                        'comentario': comentario,
                        'fecha': datetime.now().isoformat(),
                        'tipo': nuevo_estado
                    })
                
                solicitudes[i] = solicitud
                self._save_data(solicitudes)
                
                # Enviar notificación al solicitante
                self._enviar_notificacion_cambio_estado(solicitud, nuevo_estado)
                
                return solicitud
        
        return None
    
    def obtener_estadisticas(self):
        """Obtener estadísticas de las solicitudes"""
        solicitudes = self._load_data()
        
        total = len(solicitudes)
        pendientes = len([s for s in solicitudes if s['estado'] == 'pendiente'])
        aprobadas = len([s for s in solicitudes if s['estado'] == 'aprobado'])
        rechazadas = len([s for s in solicitudes if s['estado'] == 'rechazado'])
        en_revision = len([s for s in solicitudes if s['estado'] == 'en_revision'])
        
        return {
            'total': total,
            'pendientes': pendientes,
            'aprobadas': aprobadas,
            'rechazadas': rechazadas,
            'en_revision': en_revision
        }
    
    def obtener_solicitudes_por_usuario(self, usuario, tipo='solicitante'):
        """Obtener solicitudes de un usuario específico"""
        solicitudes = self._load_data()
        return [s for s in solicitudes if s[tipo] == usuario]
    
    def _enviar_notificacion_nueva_solicitud(self, solicitud):
        """Enviar notificación de nueva solicitud al responsable"""
        asunto = f"Nueva solicitud de aprobación - {solicitud['titulo']}"
        mensaje = crear_mensaje_notificacion('nueva_solicitud', solicitud)
        
        return enviar_notificacion_email(
            solicitud['responsable'] + '@gmail.com',  # Agregar dominio ficticio
            asunto,
            mensaje,
            solicitud
        )
    
    def _enviar_notificacion_cambio_estado(self, solicitud, nuevo_estado):
        """Enviar notificación de cambio de estado al solicitante"""
        asunto = f"Actualización de solicitud - {solicitud['titulo']}"
        
        if nuevo_estado == 'aprobado':
            mensaje = crear_mensaje_notificacion('solicitud_aprobada', solicitud)
        else:
            mensaje = crear_mensaje_notificacion('solicitud_rechazada', solicitud)
        
        return enviar_notificacion_email(
            solicitud['solicitante'] + '@empresa.com',  # Agregar dominio ficticio
            asunto,
            mensaje,
            solicitud
        )