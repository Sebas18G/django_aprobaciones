// JavaScript principal para el Sistema de Aprobaciones

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Aprobaciones - Cargado');
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        });
    }, 5000);
    
    // Validación en tiempo real del formulario
    setupFormValidation();
    
    // Confirmaciones para acciones importantes
    setupConfirmations();
});

// Función para validación en tiempo real
function setupFormValidation() {
    const form = document.getElementById('solicitudForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

// Validar campo individual
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Remover clases previas
    field.classList.remove('is-valid', 'is-invalid');
    
    // Validaciones específicas
    switch(field.name) {
        case 'titulo':
            if (value.length < 5) {
                isValid = false;
                errorMessage = 'El título debe tener al menos 5 caracteres';
            }
            break;
            
        case 'descripcion':
            if (value.length < 10) {
                isValid = false;
                errorMessage = 'La descripción debe tener al menos 10 caracteres';
            }
            break;
            
        case 'solicitante':
        case 'responsable':
            if (value.length < 3) {
                isValid = false;
                errorMessage = 'Debe tener al menos 3 caracteres';
            }
            break;
            
        case 'tipo_solicitud':
            if (!value) {
                isValid = false;
                errorMessage = 'Debe seleccionar un tipo de solicitud';
            }
            break;
    }
    
    // Aplicar estilos y mensajes
    if (isValid && value) {
        field.classList.add('is-valid');
        removeErrorMessage(field);
    } else if (!isValid) {
        field.classList.add('is-invalid');
        showErrorMessage(field, errorMessage);
    }
    
    return isValid;
}

// Mostrar mensaje de error
function showErrorMessage(field, message) {
    removeErrorMessage(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-error-for', field.name);
    
    field.parentNode.appendChild(errorDiv);
}

// Remover mensaje de error
function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector(`[data-error-for="${field.name}"]`);
    if (existingError) {
        existingError.remove();
    }
}

// Configurar confirmaciones
function setupConfirmations() {
    // Confirmación para acciones de eliminar (para futuras funcionalidades)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-danger') && e.target.dataset.confirm) {
            e.preventDefault();
            
            if (confirm('¿Estás seguro de que deseas realizar esta acción? Esta operación no se puede deshacer.')) {
                // Proceder con la acción
                if (e.target.href) {
                    window.location.href = e.target.href;
                } else if (e.target.form) {
                    e.target.form.submit();
                }
            }
        }
    });
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'success') {
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
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Mostrar el toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover el toast del DOM después de que se oculte
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Función para actualizar contadores (para futuras funcionalidades)
function updateCounters() {
    // Esta función se implementará cuando tengamos datos reales
    console.log('Actualizando contadores...');
}

// Función para formatear fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('es-ES', options);
}

// Función para generar colores de estado
function getStatusColor(status) {
    const colors = {
        'pendiente': 'warning',
        'aprobado': 'success',
        'rechazado': 'danger',
        'en_revision': 'info'
    };
    return colors[status] || 'secondary';
}

// Función para capitalizar texto
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}