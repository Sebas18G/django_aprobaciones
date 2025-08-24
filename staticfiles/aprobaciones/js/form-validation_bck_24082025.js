// Validaciones avanzadas para formularios

document.addEventListener('DOMContentLoaded', function() {
    // Configurar validación avanzada del formulario
    setupAdvancedFormValidation();
    
    // Configurar contador de caracteres
    setupCharacterCounters();
    
    // Configurar autocompletado de usuarios (simulado)
    setupUserAutocomplete();
});

function setupAdvancedFormValidation() {
    const form = document.getElementById('solicitudForm');
    if (!form) return;
    
    // Validación antes del envío
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateCompleteForm()) {
            // Si todo está válido, proceder con el envío
            this.submit();
        } else {
            showToast('Por favor, corrige los errores en el formulario', 'danger');
            
            // Hacer scroll al primer campo con error
            const firstError = document.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });
}

function validateCompleteForm() {
    const form = document.getElementById('solicitudForm');
    const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Validaciones específicas del negocio
    if (!validateBusinessRules()) {
        isValid = false;
    }
    
    return isValid;
}

function validateBusinessRules() {
    let isValid = true;
    
    // Validar que solicitante y responsable no sean iguales
    const solicitante = document.querySelector('[name="solicitante"]').value.trim().toLowerCase();
    const responsable = document.querySelector('[name="responsable"]').value.trim().toLowerCase();
    
    if (solicitante && responsable && solicitante === responsable) {
        showFieldError(document.querySelector('[name="responsable"]'), 
                      'El responsable no puede ser el mismo que el solicitante');
        isValid = false;
    }
    
    // Validar longitud mínima de descripción por tipo de solicitud
    const tipo = document.querySelector('[name="tipo_solicitud"]').value;
    const descripcion = document.querySelector('[name="descripcion"]').value.trim();
    
    const minimasDescripcion = {
        'despliegue': 50,
        'cambio_tecnico': 100,
        'pipeline': 75,
        'incorporacion': 80
    };
    
    const minimaRequerida = minimasDescripcion[tipo] || 10;
    if (descripcion.length < minimaRequerida) {
        showFieldError(document.querySelector('[name="descripcion"]'), 
                      `Para este tipo de solicitud, la descripción debe tener al menos ${minimaRequerida} caracteres`);
        isValid = false;
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
        
        // Crear contador
        const counter = document.createElement('div');
        counter.className = 'character-counter text-muted small mt-1';
        counter.innerHTML = `<span class="current">0</span>/${config.max} caracteres`;
        
        field.parentNode.appendChild(counter);
        
        // Actualizar contador en tiempo real
        field.addEventListener('input', function() {
            const current = this.value.length;
            const currentSpan = counter.querySelector('.current');
            currentSpan.textContent = current;
            
            // Cambiar color según proximidad al límite
            if (current > config.max * 0.9) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-warning', 'text-muted');
            } else if (current > config.max * 0.7) {
                counter.classList.add('text-warning');
                counter.classList.remove('text-danger', 'text-muted');
            } else {
                counter.classList.add('text-muted');
                counter.classList.remove('text-danger', 'text-warning');
            }
            
            // Validar límite
            if (current > config.max) {
                showFieldError(this, `Máximo ${config.max} caracteres permitidos`);
            }
        });
    });
}

function setupUserAutocomplete() {
    // Simulamos usuarios de red para autocompletado
    const usuarios = [
        'admin.sistema', 'dev.frontend', 'dev.backend', 'lead.tech', 
        'architect.solution', 'manager.project', 'qa.tester', 'devops.engineer'
    ];
    
    const userFields = document.querySelectorAll('[name="solicitante"], [name="responsable"]');
    
    userFields.forEach(field => {
        // Crear lista de sugerencias
        const suggestionsList = document.createElement('div');
        suggestionsList.className = 'user-suggestions';
        suggestionsList.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #dee2e6;
            border-top: none;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
        
        // Hacer el contenedor padre relativo
        field.parentNode.style.position = 'relative';
        field.parentNode.appendChild(suggestionsList);
        
        // Mostrar sugerencias al escribir
        field.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            
            if (value.length < 2) {
                suggestionsList.style.display = 'none';
                return;
            }
            
            const matches = usuarios.filter(user => 
                user.toLowerCase().includes(value)
            );
            
            if (matches.length === 0) {
                suggestionsList.style.display = 'none';
                return;
            }
            
            suggestionsList.innerHTML = matches.map(user => 
                `<div class="suggestion-item p-2 cursor-pointer" style="cursor: pointer; border-bottom: 1px solid #eee;" data-user="${user}">
                    <i class="fas fa-user text-muted me-2"></i>${user}
                </div>`
            ).join('');
            
            suggestionsList.style.display = 'block';
        });
        
        // Seleccionar sugerencia
        suggestionsList.addEventListener('click', function(e) {
            if (e.target.classList.contains('suggestion-item')) {
                field.value = e.target.dataset.user;
                this.style.display = 'none';
                validateField(field);
            }
        });
        
        // Ocultar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!field.contains(e.target) && !suggestionsList.contains(e.target)) {
                suggestionsList.style.display = 'none';
            }
        });
        
        // Navegar con teclado
        field.addEventListener('keydown', function(e) {
            const items = suggestionsList.querySelectorAll('.suggestion-item');
            const activeItem = suggestionsList.querySelector('.suggestion-item.active');
            let activeIndex = -1;
            
            if (activeItem) {
                activeIndex = Array.from(items).indexOf(activeItem);
            }
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    if (activeIndex < items.length - 1) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[activeIndex + 1].classList.add('active');
                        items[activeIndex + 1].style.backgroundColor = '#f8f9fa';
                    }
                    break;
                    
                case 'ArrowUp':
                    e.preventDefault();
                    if (activeIndex > 0) {
                        if (activeItem) activeItem.classList.remove('active');
                        items[activeIndex - 1].classList.add('active');
                        items[activeIndex - 1].style.backgroundColor = '#f8f9fa';
                    }
                    break;
                    
                case 'Enter':
                    if (activeItem) {
                        e.preventDefault();
                        field.value = activeItem.dataset.user;
                        suggestionsList.style.display = 'none';
                        validateField(field);
                    }
                    break;
                    
                case 'Escape':
                    suggestionsList.style.display = 'none';
                    break;
            }
        });
    });
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Remover error anterior
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Agregar nuevo error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}