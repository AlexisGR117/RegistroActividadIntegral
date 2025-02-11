# views.py
from django.shortcuts import render
from django.contrib import messages
from django.db.models import QuerySet

from .models import Actividad, Categoria
from .utils import AnalizadorActividades


def mostrar_estadisticas(request):
    """Muestra las estadísticas de actividad con filtrado."""
    analizador = AnalizadorActividades()

    parametros_filtro = {
        'nombre_usuario': request.GET.get('usuario'),
        'categoria': request.GET.get('categoria'),
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'fecha_exacta': request.GET.get('fecha_exacta'),
        'consulta_busqueda': request.GET.get('buscar_registro', '').strip(),
        'pagina': request.GET.get('page', 1)
    }

    actividades: QuerySet = Actividad.objects.all()

    usuarios_registrados = Actividad.objects.values_list(
        'usuario',
        flat=True
    ).distinct().order_by('usuario')

    contexto = {
        'usuarios_registrados': list(usuarios_registrados),
        'categorias_disponibles': Categoria.objects.exclude(id=4)
    }

    actividades = analizador.filtrar_actividades_por_usuario(
        actividades,
        nombre_usuario=parametros_filtro['nombre_usuario']
    )

    contexto.update(
        analizador.obtener_tiempos_por_categoria_ultimos_7_dias(
            actividades,
            parametros_filtro['fecha_inicio'],
            parametros_filtro['fecha_exacta']
        )
    )

    actividades = analizador.filtrar_actividades_por_fecha(
        actividades,
        parametros_filtro['fecha_inicio'],
        parametros_filtro['fecha_fin'],
        parametros_filtro['fecha_exacta']
    )

    contexto.update(
        analizador.obtener_datos_por_hora(actividades)
    )

    contexto.update(
        analizador.obtener_datos_categorias(actividades)
    )

    actividades = analizador.filtrar_actividades_por_categoria(
        actividades,
        categoria=parametros_filtro['categoria']
    )

    contexto.update(
        analizador.calcular_estadisticas_detalladas(
            actividades,
            consulta_busqueda=parametros_filtro['consulta_busqueda'],
            pagina=parametros_filtro['pagina']
        )
    )

    if not actividades.exists():
        messages.info(
            request,
            "No se encontraron resultados con los filtros proporcionados"
        )

    return render(request, 'estadisticas.html', contexto)
