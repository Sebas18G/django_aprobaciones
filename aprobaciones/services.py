# services.py - Versión actualizada para PostgreSQL
from datetime import datetime
from django.db import transaction
from django.db.models import Q, Count
from .models import SolicitudAprobacion, HistorialSolicitud, ComentarioSolicitud
from .utils import enviar_notificacion_email, crear_mensaje_notificacion

class SolicitudStorageService:
    """
    Servicio para gestionar solicitudes usando PostgreSQL
    """
    
    def crear_solicitud(self, form_data):
        """Crear una nueva solicitud en la base de datos"""
        with transaction.atomic():
            # Crear la solicitud
            nueva_solicitud = SolicitudAprobacion.objects.create(
                titulo=form_data['titulo'],
                descripcion=form_data['descripcion'],
                solicitante=form_data['solicitante'],
                responsable=form_data['responsable'],
                tipo_solicitud=form_data['tipo_solicitud'],
                estado='pendiente'
            )
            
            # Crear entrada en el historial
            HistorialSolicitud.objects.create(
                solicitud=nueva_solicitud,
                accion='creada',
                usuario=form_data['solicitante'],
                comentario='Solicitud creada'
            )
            
            # Enviar notificación al responsable
            self._enviar_notificacion_nueva_solicitud(nueva_solicitud)
            
            return self._solicitud_to_dict(nueva_solicitud)
    
    def obtener_todas_solicitudes(self):
        """Obtener todas las solicitudes con sus relaciones"""
        solicitudes = SolicitudAprobacion.objects.prefetch_related(
            'historial', 'comentarios'
        ).all()
        
        return [self._solicitud_to_dict(solicitud) for solicitud in solicitudes]
    
    def obtener_solicitud_por_id(self, solicitud_id):
        """Obtener una solicitud específica por ID"""
        try:
            solicitud = SolicitudAprobacion.objects.prefetch_related(
                'historial', 'comentarios'
            ).get(id=solicitud_id)
            
            return self._solicitud_to_dict(solicitud)
        except SolicitudAprobacion.DoesNotExist:
            return None
    
    def actualizar_solicitud(self, solicitud_id, nuevos_datos):
        """Actualizar una solicitud existente"""
        try:
            with transaction.atomic():
                solicitud = SolicitudAprobacion.objects.get(id=solicitud_id)
                
                # Actualizar campos permitidos
                campos_actualizables = ['titulo', 'descripcion', 'tipo_solicitud']
                for campo in campos_actualizables:
                    if campo in nuevos_datos:
                        setattr(solicitud, campo, nuevos_datos[campo])
                
                solicitud.save()
                
                # Agregar entrada al historial
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    accion='actualizada',
                    usuario=nuevos_datos.get('usuario_actualizacion', solicitud.solicitante),
                    comentario='Solicitud actualizada'
                )
                
                return self._solicitud_to_dict(solicitud)
        except SolicitudAprobacion.DoesNotExist:
            return None
    
    def aprobar_solicitud(self, solicitud_id, aprobador, comentario=''):
        """Aprobar una solicitud"""
        return self._cambiar_estado_solicitud(solicitud_id, 'aprobado', aprobador, comentario)
    
    def rechazar_solicitud(self, solicitud_id, aprobador, comentario=''):
        """Rechazar una solicitud"""
        return self._cambiar_estado_solicitud(solicitud_id, 'rechazado', aprobador, comentario)
    
    def _cambiar_estado_solicitud(self, solicitud_id, nuevo_estado, usuario, comentario=''):
        """Cambiar el estado de una solicitud"""
        try:
            with transaction.atomic():
                solicitud = SolicitudAprobacion.objects.get(id=solicitud_id)
                estado_anterior = solicitud.estado
                
                # Actualizar estado
                solicitud.estado = nuevo_estado
                solicitud.save()
                
                # Agregar entrada al historial
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    accion=nuevo_estado,
                    usuario=usuario,
                    comentario=comentario or f'Solicitud {nuevo_estado}',
                    estado_anterior=estado_anterior
                )
                
                # Agregar comentario si existe
                if comentario:
                    ComentarioSolicitud.objects.create(
                        solicitud=solicitud,
                        usuario=usuario,
                        comentario=comentario,
                        tipo=nuevo_estado
                    )
                
                # Enviar notificación al solicitante
                self._enviar_notificacion_cambio_estado(solicitud, nuevo_estado)
                
                return self._solicitud_to_dict(solicitud)
        except SolicitudAprobacion.DoesNotExist:
            return None
    
    def obtener_estadisticas(self):
        """Obtener estadísticas de las solicitudes usando agregación de Django"""
        estadisticas = SolicitudAprobacion.objects.aggregate(
            total=Count('id'),
            pendientes=Count('id', filter=Q(estado='pendiente')),
            aprobadas=Count('id', filter=Q(estado='aprobado')),
            rechazadas=Count('id', filter=Q(estado='rechazado')),
            en_revision=Count('id', filter=Q(estado='en_revision'))
        )
        
        return estadisticas
    
    def obtener_solicitudes_por_usuario(self, usuario, tipo='solicitante'):
        """Obtener solicitudes de un usuario específico"""
        if tipo == 'solicitante':
            solicitudes = SolicitudAprobacion.objects.filter(
                solicitante=usuario
            ).prefetch_related('historial', 'comentarios')
        else:
            solicitudes = SolicitudAprobacion.objects.filter(
                responsable=usuario
            ).prefetch_related('historial', 'comentarios')
        
        return [self._solicitud_to_dict(solicitud) for solicitud in solicitudes]
    
    def filtrar_solicitudes(self, estado=None, tipo=None, solicitante=None, responsable=None):
        """Filtrar solicitudes con múltiples criterios"""
        queryset = SolicitudAprobacion.objects.prefetch_related('historial', 'comentarios')
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo:
            queryset = queryset.filter(tipo_solicitud=tipo)
        if solicitante:
            queryset = queryset.filter(solicitante=solicitante)
        if responsable:
            queryset = queryset.filter(responsable=responsable)
        
        return [self._solicitud_to_dict(solicitud) for solicitud in queryset]
    
    def _solicitud_to_dict(self, solicitud):
        """Convertir modelo SolicitudAprobacion a diccionario para compatibilidad"""
        return {
            'id': str(solicitud.id),
            'titulo': solicitud.titulo,
            'descripcion': solicitud.descripcion,
            'solicitante': solicitud.solicitante,
            'responsable': solicitud.responsable,
            'tipo_solicitud': solicitud.tipo_solicitud,
            'estado': solicitud.estado,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_actualizacion': solicitud.fecha_actualizacion.isoformat(),
            'historial': [
                {
                    'accion': h.accion,
                    'usuario': h.usuario,
                    'fecha': h.fecha.isoformat(),
                    'comentario': h.comentario,
                    'estado_anterior': h.estado_anterior
                }
                for h in solicitud.historial_ordenado
            ],
            'comentarios': [
                {
                    'usuario': c.usuario,
                    'comentario': c.comentario,
                    'fecha': c.fecha.isoformat(),
                    'tipo': c.tipo
                }
                for c in solicitud.comentarios_ordenados
            ]
        }
    
    def _enviar_notificacion_nueva_solicitud(self, solicitud):
        """Enviar notificación de nueva solicitud al responsable"""
        solicitud_dict = self._solicitud_to_dict(solicitud)
        asunto = f"Nueva solicitud de aprobación - {solicitud.titulo}"
        mensaje = crear_mensaje_notificacion('nueva_solicitud', solicitud_dict)
        
        return enviar_notificacion_email(
            solicitud.responsable + '@gmail.com',
            asunto,
            mensaje,
            solicitud_dict
        )
    
    def _enviar_notificacion_cambio_estado(self, solicitud, nuevo_estado):
        """Enviar notificación de cambio de estado al solicitante"""
        solicitud_dict = self._solicitud_to_dict(solicitud)
        asunto = f"Actualización de solicitud - {solicitud.titulo}"
        
        if nuevo_estado == 'aprobado':
            mensaje = crear_mensaje_notificacion('solicitud_aprobada', solicitud_dict)
        else:
            mensaje = crear_mensaje_notificacion('solicitud_rechazada', solicitud_dict)
        
        return enviar_notificacion_email(
            solicitud.solicitante + '@empresa.com',
            asunto,
            mensaje,
            solicitud_dict
        )