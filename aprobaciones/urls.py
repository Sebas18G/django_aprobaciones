# urls.py - URLs para el módulo de aprobaciones

from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de solicitudes
    path('crear/', views.crear_solicitud, name='crear_solicitud'),
    path('listar/', views.listar_solicitudes, name='listar_solicitudes'),
    path('solicitud/<str:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    
    # Acciones de aprobación/rechazo
    path('solicitud/<str:solicitud_id>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitud/<str:solicitud_id>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitud/<str:solicitud_id>/cambiar-estado/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
]