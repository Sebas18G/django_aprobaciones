import os
import sys
from django.core.wsgi import get_wsgi_application

# Añadir el directorio del proyecto al path de Python
project_path = r'C:\Users\jhoan\Documents\venv_prueba_tecnica\project_app'
sys.path.insert(0, project_path)

# Cambiar al directorio del proyecto
os.chdir(project_path)

# Configurar Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_app.settings')  # Asumiendo que el proyecto se llama 'project_app'

# Obtener la aplicación WSGI
application = get_wsgi_application()