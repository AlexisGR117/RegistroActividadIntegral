
from django.urls import path
from . import views

urlpatterns = [
    path(
        'estadisticas/',
        views.mostrar_estadisticas,
        name='estadisticas'
    )
]
