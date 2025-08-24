# models.py
from django.db import models
from django.utils import timezone
import uuid
from .constants import ESTADOS_SOLICITUD, TIPOS_SOLICITUD

class SolicitudAprobacion(models.Model):
    """
    Modelo principal para las solicitudes de aprobación
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='ID único de la solicitud'
    )
    
    titulo = models.CharField(
        max_length=200,
        help_text='Título de la solicitud'
    )
    
    descripcion = models.TextField(
        help_text='Descripción detallada de la solicitud'
    )
    
    solicitante = models.CharField(
        max_length=100,
        help_text='Usuario de red del solicitante'
    )
    
    responsable = models.CharField(
        max_length=100,
        help_text='Usuario de red del responsable de aprobar'
    )
    
    tipo_solicitud = models.CharField(
        max_length=20,
        choices=TIPOS_SOLICITUD,
        help_text='Tipo de solicitud'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_SOLICITUD,
        default='pendiente',
        help_text='Estado actual de la solicitud'
    )
    
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text='Fecha y hora de última actualización'
    )
    
    class Meta:
        verbose_name = 'Solicitud de Aprobación'
        verbose_name_plural = 'Solicitudes de Aprobación'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_solicitud']),
            models.Index(fields=['solicitante']),
            models.Index(fields=['responsable']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    @property
    def historial_ordenado(self):
        """Retorna el historial ordenado por fecha"""
        return self.historial.all().order_by('fecha')
    
    @property
    def comentarios_ordenados(self):
        """Retorna los comentarios ordenados por fecha"""
        return self.comentarios.all().order_by('fecha')


class HistorialSolicitud(models.Model):
    """
    Modelo para el historial de cambios de una solicitud
    """
    solicitud = models.ForeignKey(
        SolicitudAprobacion,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    
    accion = models.CharField(
        max_length=50,
        help_text='Acción realizada (creada, aprobada, rechazada, etc.)'
    )
    
    usuario = models.CharField(
        max_length=100,
        help_text='Usuario que realizó la acción'
    )
    
    fecha = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de la acción'
    )
    
    comentario = models.TextField(
        blank=True,
        help_text='Comentario o descripción de la acción'
    )
    
    estado_anterior = models.CharField(
        max_length=20,
        blank=True,
        help_text='Estado anterior antes del cambio'
    )
    
    class Meta:
        verbose_name = 'Entrada de Historial'
        verbose_name_plural = 'Entradas de Historial'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.solicitud.titulo} - {self.accion} por {self.usuario}"


class ComentarioSolicitud(models.Model):
    """
    Modelo para comentarios en las solicitudes
    """
    solicitud = models.ForeignKey(
        SolicitudAprobacion,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )
    
    usuario = models.CharField(
        max_length=100,
        help_text='Usuario que hizo el comentario'
    )
    
    comentario = models.TextField(
        help_text='Contenido del comentario'
    )
    
    fecha = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora del comentario'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General'),
            ('aprobado', 'Aprobación'),
            ('rechazado', 'Rechazo'),
            ('revision', 'Revisión'),
        ],
        default='general',
        help_text='Tipo de comentario'
    )
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Comentario de {self.usuario} en {self.solicitud.titulo}"