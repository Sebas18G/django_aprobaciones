# admin.py
from django.contrib import admin
from .models import SolicitudAprobacion, HistorialSolicitud, ComentarioSolicitud

class HistorialInline(admin.TabularInline):
    model = HistorialSolicitud
    extra = 0
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)

class ComentarioInline(admin.TabularInline):
    model = ComentarioSolicitud
    extra = 0
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)

@admin.register(SolicitudAprobacion)
class SolicitudAprobacionAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 
        'solicitante', 
        'responsable', 
        'tipo_solicitud', 
        'estado',
        'fecha_creacion',
        'fecha_actualizacion'
    )
    
    list_filter = (
        'estado',
        'tipo_solicitud',
        'fecha_creacion',
    )
    
    search_fields = (
        'titulo',
        'solicitante',
        'responsable',
        'descripcion'
    )
    
    readonly_fields = (
        'id',
        'fecha_creacion',
        'fecha_actualizacion'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'titulo', 'descripcion')
        }),
        ('Usuarios', {
            'fields': ('solicitante', 'responsable')
        }),
        ('Clasificación', {
            'fields': ('tipo_solicitud', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [HistorialInline, ComentarioInline]
    
    date_hierarchy = 'fecha_creacion'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'historial', 'comentarios'
        )

@admin.register(HistorialSolicitud)
class HistorialSolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'solicitud',
        'accion',
        'usuario',
        'fecha',
        'estado_anterior'
    )
    
    list_filter = (
        'accion',
        'fecha',
        'usuario'
    )
    
    search_fields = (
        'solicitud__titulo',
        'usuario',
        'comentario'
    )
    
    readonly_fields = ('fecha',)
    
    date_hierarchy = 'fecha'

@admin.register(ComentarioSolicitud)
class ComentarioSolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'solicitud',
        'usuario',
        'tipo',
        'fecha'
    )
    
    list_filter = (
        'tipo',
        'fecha',
        'usuario'
    )
    
    search_fields = (
        'solicitud__titulo',
        'usuario',
        'comentario'
    )
    
    readonly_fields = ('fecha',)
    
    date_hierarchy = 'fecha'