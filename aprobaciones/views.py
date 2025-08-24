from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .forms import SolicitudAprobacionForm
from .services import SolicitudStorageService
from .utils import obtener_color_estado, formatear_tipo_solicitud

#views.py

def crear_solicitud(request):
    """Vista para crear una nueva solicitud de aprobación"""
    storage = SolicitudStorageService()
    
    if request.method == 'POST':
        form = SolicitudAprobacionForm(request.POST)
        if form.is_valid():
            try:
                # Crear solicitud usando el servicio de almacenamiento
                nueva_solicitud = storage.crear_solicitud(form.cleaned_data)
                
                # Mensaje de éxito
                messages.success(
                    request, 
                    f'Solicitud creada exitosamente con ID: {nueva_solicitud["id"]}'
                )
                
                # Si es una petición AJAX, devolver JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Solicitud creada exitosamente',
                        'solicitud_id': nueva_solicitud["id"]
                    })
                
                return redirect('dashboard')  # Redirigir al dashboard para ver la solicitud
                
            except Exception as e:
                messages.error(request, f'Error al crear la solicitud: {str(e)}')
        else:
            # Si hay errores y es AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = SolicitudAprobacionForm()
    
    return render(request, 'aprobaciones/crear_solicitud.html', {
        'form': form,
        'titulo_pagina': 'Crear Solicitud de Aprobación'
    })

def dashboard(request):
    """Vista principal del dashboard"""
    storage = SolicitudStorageService()
    
    # Obtener estadísticas
    estadisticas = storage.obtener_estadisticas()
    
    # Obtener solicitudes recientes (últimas 10)
    todas_solicitudes = storage.obtener_todas_solicitudes()
    
    # Ordenar por fecha de creación (más recientes primero)
    solicitudes_ordenadas = sorted(
        todas_solicitudes, 
        key=lambda x: x['fecha_creacion'], 
        reverse=True
    )
    
    # Tomar las 10 más recientes para el dashboard
    solicitudes_recientes = solicitudes_ordenadas[:10]
    
    # Agregar información adicional a cada solicitud
    for solicitud in solicitudes_recientes:
        solicitud['color_estado'] = obtener_color_estado(solicitud['estado'])
        solicitud['tipo_formateado'] = formatear_tipo_solicitud(solicitud['tipo_solicitud'])
        
        # Formatear fecha
        from datetime import datetime
        try:
            fecha = datetime.fromisoformat(solicitud['fecha_creacion'].replace('Z', '+00:00'))
            solicitud['fecha_formateada'] = fecha.strftime('%d/%m/%Y %H:%M')
        except:
            solicitud['fecha_formateada'] = 'Fecha no disponible'
    
    return render(request, 'aprobaciones/dashboard.html', {
        'titulo_pagina': 'Dashboard - Sistema de Aprobaciones',
        'estadisticas': estadisticas,
        'solicitudes_recientes': solicitudes_recientes
    })

def detalle_solicitud(request, solicitud_id):
    """Vista para ver el detalle de una solicitud"""
    storage = SolicitudStorageService()
    solicitud = storage.obtener_solicitud_por_id(solicitud_id)
    
    if not solicitud:
        messages.error(request, 'La solicitud solicitada no fue encontrada')
        return redirect('dashboard')
    
    # Agregar información adicional
    solicitud['color_estado'] = obtener_color_estado(solicitud['estado'])
    solicitud['tipo_formateado'] = formatear_tipo_solicitud(solicitud['tipo_solicitud'])
    
    # Formatear fechas en el historial
    from datetime import datetime
    for entrada in solicitud['historial']:
        try:
            fecha = datetime.fromisoformat(entrada['fecha'].replace('Z', '+00:00'))
            entrada['fecha_formateada'] = fecha.strftime('%d/%m/%Y %H:%M')
        except:
            entrada['fecha_formateada'] = 'Fecha no disponible'
    
    return render(request, 'aprobaciones/detalle_solicitud.html', {
        'titulo_pagina': f'Solicitud - {solicitud["titulo"]}',
        'solicitud': solicitud
    })

def listar_solicitudes(request):
    """Vista para listar todas las solicitudes con filtros"""
    storage = SolicitudStorageService()
    
    # Obtener todas las solicitudes
    todas_solicitudes = storage.obtener_todas_solicitudes()
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    solicitudes_filtradas = todas_solicitudes
    
    if estado_filtro:
        solicitudes_filtradas = [s for s in solicitudes_filtradas if s['estado'] == estado_filtro]
    
    if tipo_filtro:
        solicitudes_filtradas = [s for s in solicitudes_filtradas if s['tipo_solicitud'] == tipo_filtro]
    
    # Ordenar por fecha de creación (más recientes primero)
    solicitudes_filtradas = sorted(
        solicitudes_filtradas, 
        key=lambda x: x['fecha_creacion'], 
        reverse=True
    )
    
    # Paginación
    paginator = Paginator(solicitudes_filtradas, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Agregar información adicional a cada solicitud
    for solicitud in page_obj:
        solicitud['color_estado'] = obtener_color_estado(solicitud['estado'])
        solicitud['tipo_formateado'] = formatear_tipo_solicitud(solicitud['tipo_solicitud'])
        
        # Formatear fecha
        from datetime import datetime
        try:
            fecha = datetime.fromisoformat(solicitud['fecha_creacion'].replace('Z', '+00:00'))
            solicitud['fecha_formateada'] = fecha.strftime('%d/%m/%Y %H:%M')
        except:
            solicitud['fecha_formateada'] = 'Fecha no disponible'
    
    return render(request, 'aprobaciones/listar_solicitudes.html', {
        'titulo_pagina': 'Todas las Solicitudes',
        'page_obj': page_obj,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro
    })

@require_http_methods(["POST"])
def aprobar_solicitud(request, solicitud_id):
    """Vista para aprobar una solicitud"""
    storage = SolicitudStorageService()
    
    try:
        # Obtener datos del POST
        data = json.loads(request.body) if request.body else {}
        comentario = data.get('comentario', '')
        
        # Por ahora usar un usuario fijo, en producción usar request.user.username
        aprobador = 'usuario_actual'  # TODO: cambiar por request.user.username
        
        # Aprobar solicitud usando el servicio
        solicitud_actualizada = storage.aprobar_solicitud(
            solicitud_id, 
            aprobador, 
            comentario
        )
        
        if solicitud_actualizada:
            messages.success(request, 'Solicitud aprobada exitosamente')
            
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Solicitud aprobada exitosamente',
                    'nuevo_estado': 'aprobado',
                    'solicitud': solicitud_actualizada
                })
            
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
        else:
            messages.error(request, 'No se pudo encontrar la solicitud')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo encontrar la solicitud'
                })
                
            return redirect('dashboard')
            
    except Exception as e:
        messages.error(request, f'Error al aprobar la solicitud: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al aprobar la solicitud: {str(e)}'
            })
        
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)

@require_http_methods(["POST"])
def rechazar_solicitud(request, solicitud_id):
    """Vista para rechazar una solicitud"""
    storage = SolicitudStorageService()
    
    try:
        # Obtener datos del POST
        data = json.loads(request.body) if request.body else {}
        comentario = data.get('comentario', 'Solicitud rechazada sin comentarios')
        
        # Por ahora usar un usuario fijo, en producción usar request.user.username
        aprobador = 'usuario_actual'  # TODO: cambiar por request.user.username
        
        # Rechazar solicitud usando el servicio
        solicitud_actualizada = storage.rechazar_solicitud(
            solicitud_id, 
            aprobador, 
            comentario
        )
        
        if solicitud_actualizada:
            messages.success(request, 'Solicitud rechazada exitosamente')
            
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Solicitud rechazada exitosamente',
                    'nuevo_estado': 'rechazado',
                    'solicitud': solicitud_actualizada
                })
            
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
        else:
            messages.error(request, 'No se pudo encontrar la solicitud')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo encontrar la solicitud'
                })
                
            return redirect('dashboard')
            
    except Exception as e:
        messages.error(request, f'Error al rechazar la solicitud: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al rechazar la solicitud: {str(e)}'
            })
        
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)

@require_http_methods(["POST"])
def cambiar_estado_solicitud(request, solicitud_id):
    """Vista genérica para cambiar estado de solicitud"""
    storage = SolicitudStorageService()
    
    try:
        data = json.loads(request.body) if request.body else {}
        nuevo_estado = data.get('estado')
        comentario = data.get('comentario', '')
        usuario = 'usuario_actual'  # TODO: cambiar por request.user.username
        
        if not nuevo_estado:
            raise ValueError("Estado requerido")
        
        # Usar el método apropiado según el estado
        if nuevo_estado == 'aprobado':
            solicitud_actualizada = storage.aprobar_solicitud(solicitud_id, usuario, comentario)
        elif nuevo_estado == 'rechazado':
            solicitud_actualizada = storage.rechazar_solicitud(solicitud_id, usuario, comentario)
        else:
            solicitud_actualizada = storage._cambiar_estado_solicitud(
                solicitud_id, nuevo_estado, usuario, comentario
            )
        
        if solicitud_actualizada:
            messages.success(request, f'Estado cambiado a {nuevo_estado} exitosamente')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Estado cambiado a {nuevo_estado} exitosamente',
                    'nuevo_estado': nuevo_estado,
                    'solicitud': solicitud_actualizada
                })
            
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
        else:
            raise ValueError("No se pudo actualizar la solicitud")
            
    except Exception as e:
        messages.error(request, f'Error al cambiar estado: {str(e)}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al cambiar estado: {str(e)}'
            })
        
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)