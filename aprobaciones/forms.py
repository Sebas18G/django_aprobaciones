from django import forms

#forms.py

class SolicitudAprobacionForm(forms.Form):

    TIPOS_SOLICITUD = [
        ('despliegue', 'Despliegue'),
        ('acceso', 'Acceso a Herramientas'),
        ('cambio_tecnico', 'Cambio Técnico'),
        ('pipeline', 'Cambios en Pipeline/CI-CD'),
        ('incorporacion', 'Nueva Incorporación Técnica'),
        ('otro', 'Otro'),
    ]
    
    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el título de la solicitud'
        })
    )
    
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describa detalladamente su solicitud',
            'rows': 5
        })
    )
    
    solicitante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario de red del solicitante'
        }),
        help_text='Usuario de red de quien hace la solicitud'
    )
    
    responsable = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario de red del responsable'
        }),
        help_text='Usuario de red de quien debe aprobar'
    )
    
    tipo_solicitud = forms.ChoiceField(
        choices=TIPOS_SOLICITUD,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if len(titulo) < 5:
            raise forms.ValidationError('El título debe tener al menos 5 caracteres')
        return titulo
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres')
        return descripcion