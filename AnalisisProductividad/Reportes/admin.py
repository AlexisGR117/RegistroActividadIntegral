from django.contrib import admin
from .models import Categoria, ActividadCategoria

admin.site.site_header = 'Análisis de Productividad'
admin.site.site_title = 'Análisis de Productividad'

admin.site.register(Categoria)
admin.site.register(ActividadCategoria)
