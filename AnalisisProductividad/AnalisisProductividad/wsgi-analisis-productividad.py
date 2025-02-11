import os
import sys

DJANGO_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.append(DJANGO_PATH)
sys.path.append(
    r'C:\Users\AlexisGR117\Desktop\RegistroActividadIntegral'
    r'\AnalisisProductividad\VENV_ANALISIS_PRODUCTIVIDAD\Scripts')
sys.path.append(
    r'C:\Users\AlexisGR117\Desktop\RegistroActividadIntegral'
    r'\AnalisisProductividad\VENV_ANALISIS_PRODUCTIVIDAD\Lib\site-packages')
activate_this = (
    r'C:\Users\AlexisGR117\Desktop\RegistroActividadIntegral\AnalisisProductividad'
    r'\VENV_ANALISIS_PRODUCTIVIDAD\Scripts\activate_this.py'
)

with open(activate_this, encoding='utf-8') as f:
    import runpy
    runpy.run_path(activate_this, run_name="__main__")

os.environ['DJANGO_SETTINGS_MODULE'] = 'AnalisisProductividad.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
