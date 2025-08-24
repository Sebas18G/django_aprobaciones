// JavaScript corregido para el sistema de aprobaciones

// Configuración inicial
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Aprobaciones - Cargado');
    
    // Inicializar tooltips de Bootstrap si existe
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            if (typeof bootstrap !== 'undefined') {
                var alertInstance = new bootstrap.Alert(alert);
                alertInstance.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 5000);
    
    // Configurar CSRF token
    setupCSRFToken();
});

// FUNCIONES PRINCIPALES - Definidas globalmente
function aprobarSolicitud(solicitudId, comentario = '') {
    console.log('Aprobando solicitud:', solicitudId);
    
    if (!confirm('¿Estás seguro de que deseas aprobar esta solicitud?')) {
        return;
    }
    
    let comentarioFinal = comentario;
    if (!comentarioFinal) {
        comentarioFinal = prompt('Comentario adicional (opcional):') || '';
    }
    
    realizarCambioEstado(solicitudId, 'aprobar', comentarioFinal);
}

function rechazarSolicitud(solicitudId, comentario = '') {
    console.log('Rechazando solicitud:', solicitudId);
    
    let comentarioFinal = comentario;
    if (!comentarioFinal) {
        comentarioFinal = prompt('¿Por qué rechazas esta solicitud? (recomendado):');
        if (comentarioFinal === null) {
            return; // Usuario canceló
        }
    }
    
    if (!confirm('¿Estás seguro de que deseas rechazar esta solicitud?')) {
        return;
    }
    
    realizarCambioEstado(solicitudId, 'rechazar', comentarioFinal || 'Solicitud rechazada sin comentarios');
}

function realizarCambioEstado(solicitudId, accion, comentario = '') {
    console.log('Realizando cambio de estado:', { solicitudId, accion, comentario });

    const loadingMessage = mostrarIndicadorCarga(`${accion === 'aprobar' ? 'Aprobando' : 'Rechazando'} solicitud...`);

    let url, estado;
    if (accion === 'aprobar') {
        url = urlAprobar;
        estado = 'aprobado';
    } else if (accion === 'rechazar') {
        url = urlRechazar;
        estado = 'rechazado';
    } else {
        console.error('Acción no válida:', accion);
        ocultarIndicadorCarga(loadingMessage);
        showToast('Acción no válida', 'danger');
        return;
    }

    const datos = { comentario };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(datos)
    })
    .then(response => {
        console.log('Respuesta recibida:', response.status, response.statusText);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        return response.json();
    })
    .then(data => {
        console.log('Datos recibidos:', data);
        ocultarIndicadorCarga(loadingMessage);

        if (data.success) {
            showToast(data.message, 'success');
            actualizarInterfazSolicitud(solicitudId, estado, data.solicitud);

            setTimeout(() => window.location.reload(), 2000);
        } else {
            showToast(data.message || 'Error desconocido', 'danger');
        }
    })
    .catch(error => {
        ocultarIndicadorCarga(loadingMessage);
        console.error('Error en la petición:', error);
        showToast(`Error al ${accion} la solicitud: ${error.message}`, 'danger');
    });
}


// Configurar CSRF token para AJAX
function setupCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     getCookie('csrftoken');
    
    if (csrfToken) {
        const meta = document.createElement('meta');
        meta.name = 'csrf-token';
        meta.content = csrfToken;
        document.head.appendChild(meta);
    }
}

// Función para obtener cookie (para CSRF)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Actualizar elementos de la interfaz después del cambio de estado
function actualizarInterfazSolicitud(solicitudId, nuevoEstado, solicitudData) {
    // Actualizar badges de estado
    const estadoBadges = document.querySelectorAll(`[data-solicitud-id="${solicitudId}"] .badge, .badge[data-estado]`);
    estadoBadges.forEach(badge => {
        const color = getStatusColor(nuevoEstado);
        badge.className = `badge bg-${color} fs-5 p-3`;
        badge.innerHTML = getStatusIcon(nuevoEstado) + ' ' + nuevoEstado.toUpperCase();
        badge.setAttribute('data-estado', nuevoEstado);
    });
    
    // Ocultar botones de acción si la solicitud ya no está pendiente
    if (nuevoEstado !== 'pendiente') {
        const botonesAprobar = document.querySelectorAll(`button[onclick*="aprobarSolicitud('${solicitudId}')"]`);
        const botonesRechazar = document.querySelectorAll(`button[onclick*="rechazarSolicitud('${solicitudId}')"]`);
        
        botonesAprobar.forEach(btn => btn.style.display = 'none');
        botonesRechazar.forEach(btn => btn.style.display = 'none');
    }
    
    // Actualizar contadores si estamos en el dashboard
    if (window.location.pathname.includes('dashboard')) {
        setTimeout(actualizarContadoresEstadisticas, 1000);
    }
}

// Mostrar indicador de carga
function mostrarIndicadorCarga(mensaje) {
    // Remover indicador anterior si existe
    const existingIndicator = document.getElementById('loading-indicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.className = 'position-fixed top-50 start-50 translate-middle bg-white p-4 rounded shadow border';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2 mb-0">${mensaje}</p>
        </div>
    `;
    
    document.body.appendChild(loadingDiv);
    return loadingDiv;
}

// Ocultar indicador de carga
function ocultarIndicadorCarga(loadingElement) {
    if (loadingElement && loadingElement.parentNode) {
        loadingElement.parentNode.removeChild(loadingElement);
    }
    // También intentar remover por ID como backup
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'success') {
    console.log(`Mostrando toast: ${type} - ${message}`);
    
    // Si Bootstrap no está disponible, usar alert como fallback
    if (typeof bootstrap === 'undefined') {
        alert(`${type.toUpperCase()}: ${message}`);
        return;
    }
    
    // Crear el contenedor de toasts si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const iconMap = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Mostrar el toast
    try {
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
        
        // Remover el toast del DOM después de que se oculte
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    } catch (error) {
        console.error('Error mostrando toast:', error);
        alert(`${type.toUpperCase()}: ${message}`);
        toast.remove();
    }
}

// Funciones auxiliares
function getStatusColor(status) {
    const colors = {
        'pendiente': 'warning',
        'aprobado': 'success',
        'rechazado': 'danger',
        'en_revision': 'info',
        'cancelado': 'secondary'
    };
    return colors[status] || 'secondary';
}

function getStatusIcon(status) {
    const icons = {
        'pendiente': '<i class="fas fa-hourglass-half"></i>',
        'aprobado': '<i class="fas fa-check-circle"></i>',
        'rechazado': '<i class="fas fa-times-circle"></i>',
        'en_revision': '<i class="fas fa-eye"></i>',
        'cancelado': '<i class="fas fa-ban"></i>'
    };
    return icons[status] || '<i class="fas fa-question-circle"></i>';
}

function actualizarContadoresEstadisticas() {
    console.log('Actualizando estadísticas...');
    // Implementar lógica para actualizar contadores
}

// Hacer funciones disponibles globalmente
window.aprobarSolicitud = aprobarSolicitud;
window.rechazarSolicitud = rechazarSolicitud;
window.showToast = showToast;