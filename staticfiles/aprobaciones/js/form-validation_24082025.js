// form-validation.js - Versión corregida

document.addEventListener('DOMContentLoaded', function() {
    // Configurar validación del formulario (simplificada)
    setupFormValidation();
    
    // Configurar contador de caracteres
    setupCharacterCounters();
    
    // Configurar autocompletado de usuarios (simplificado)
    setupUserAutocomplete();
});

function setupFormValidation() {
    const form = document.getElementById('solicitudForm');
    if (!form) return;
    
    // Solo validar campos individuales, NO prevenir el envío
    const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    fields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(field);
        });
        
        field.addEventListener('input', function() {
            // Limpiar errores mientras escribe
            if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                removeFieldError(this);
            }
        });
    });
    
    // PERMITIR que el formulario se envíe normalmente
    // Solo mostrar un mensaje de confirmación
    form.addEventListener('submit', function(e) {
        console.log('Formulario enviándose...'); // Para debug
        // NO usar e.preventDefault() aquí
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Validaciones básicas y permisivas
    switch(field.name) {
        case 'titulo':
            if (value.length < 3) { // Reducido de 5 a 3
                isValid = false;
                errorMessage = 'El título debe tener al menos 3 caracteres';
            }
            break;
            
        case 'descripcion':
            if (value.length < 5) { // Reducido de 10 a 5
                isValid = false;
                errorMessage = 'La descripción debe tener al menos 5 caracteres';
            }
            break;
            
        case 'solicitante':
        case 'responsable':
            if (value.length < 2) { // Reducido de 3 a 2
                isValid = false;
                errorMessage = 'Debe tener al menos 2 caracteres';
            }
            break;
            
        case 'tipo_solicitud':
            if (!value) {
                isValid = false;
                errorMessage = 'Debe seleccionar un tipo de solicitud';
            }
            break;
    }
    
    // Aplicar estilos
    if (isValid && value) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        removeFieldError(field);
    } else if (!isValid) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function setupCharacterCounters() {
    const fields = [
        { name: 'titulo', max: 200 },
        { name: 'descripcion', max: 2000 }
    ];
    
    fields.forEach(config => {
        const field = document.querySelector(`[name="${config.name}"]`);
        if (!field) return;
        
        // Solo mostrar contador, sin validaciones estrictas
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted small mt-1';
        counter.innerHTML = `<span class="current">0</span>/${config.max} caracteres`;
        
        field.parentNode.appendChild(counter);
        
        field.addEventListener('input', function() {
            const current = this.value.length;
            const currentSpan = counter.querySelector('.current');
            currentSpan.textContent = current;
            
            // Solo cambiar colores, no bloquear
            if (current > config.max * 0.9) {
                counter.classList.add('text-warning');
                counter.classList.remove('text-muted');
            } else {
                counter.classList.add('text-muted');
                counter.classList.remove('text-warning');
            }
        });
    });
}

function setupUserAutocomplete() {
    // Versión simplificada del autocompletado
    const usuarios = [
        'Jhoan Sanchez', 'jsan136', 'admin.sistema', 'dev.frontend', 
        'dev.backend', 'lead.tech', 'manager.project'
    ];
    
    const userFields = document.querySelectorAll('[name="solicitante"], [name="responsable"]');
    
    userFields.forEach(field => {
        // Crear lista de sugerencias simple
        const datalist = document.createElement('datalist');
        datalist.id = field.name + '_suggestions';
        
        usuarios.forEach(user => {
            const option = document.createElement('option');
            option.value = user;
            datalist.appendChild(option);
        });
        
        // Agregar datalist al campo
        field.setAttribute('list', datalist.id);
        field.parentNode.appendChild(datalist);
    });
}

function showFieldError(field, message) {
    removeFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-error-for', field.name);
    
    field.parentNode.appendChild(errorDiv);
}

function removeFieldError(field) {
    const existingError = field.parentNode.querySelector(`[data-error-for="${field.name}"]`);
    if (existingError) {
        existingError.remove();
    }
}

function showToast(message, type = 'success') {
    console.log(`Toast ${type}: ${message}`);
    // Implementación simplificada
    alert(message);
}