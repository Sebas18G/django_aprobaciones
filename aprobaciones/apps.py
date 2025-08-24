from django.apps import AppConfig


class AprobacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aprobaciones'
    verbose_name = 'Sistema de Aprobaciones'
    
    def ready(self):
        # Aquí podemos importar señales cuando las implementemos
        pass