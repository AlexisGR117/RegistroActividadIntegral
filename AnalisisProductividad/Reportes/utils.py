# utils.py
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Union, TypedDict

import pytz
import logging
from django.db.models import QuerySet, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings

from .models import Categoria, ActividadCategoria


class CategoriaData(TypedDict):
    categoria: str
    tiempo: float
    porcentaje: float


class ChartData(TypedDict):
    label: str
    data: List[float]


class ClasificadorActividades:
    """Clasifica actividades según proceso y título de ventana."""

    CACHE_TTL = getattr(settings, 'CATEGORIA_CACHE_TTL', 3600)

    def __init__(self):
        self._inicializar_categorias()

    @lru_cache(maxsize=1)
    def _inicializar_categorias(self) -> None:
        """Inicializa y cachea las categorías."""
        self.CATEGORIAS = {
            'CONFIGURACIONES': self._obtener_procesos_categoria(5),
            'JUEGOS': self._obtener_procesos_categoria(3),
            'TITULOS_ENTRETENIMIENTO': self._obtener_titulos_categoria(2),
            'PROCESOS_ENTRETENIMIENTO': self._obtener_procesos_categoria(
                2, True
            ),
            'TITULOS_TRABAJO_ESTUDIO': self._obtener_titulos_categoria(1),
            'PROCESOS_TRABAJO_ESTUDIO': self._obtener_procesos_categoria(1),
            'PROCESOS_INACTIVOS': self._obtener_procesos_categoria(6),
            'NAVEGADORES': self._obtener_procesos_categoria(4)
        }

    def _obtener_procesos_categoria(
        self,
        id_categoria: int,
        usar_proceso: bool = False
    ) -> List[str]:
        """Recuperar procesos para una categoría específica."""
        return list(
            ActividadCategoria.objects
            .filter(categoria=id_categoria)
            .filter(Q(nombre_proceso__isnull=False))
            .filter(Q(titulo_ventana__isnull=True) if usar_proceso else Q())
            .values_list('nombre_proceso', flat=True)
            .distinct()
        )

    def _obtener_titulos_categoria(self, id_categoria: int) -> List[str]:
        """Recuperar títulos para una categoría específica."""
        return list(
            ActividadCategoria.objects
            .filter(categoria=id_categoria)
            .exclude(titulo_ventana__isnull=True)
            .values_list('titulo_ventana', flat=True)
            .distinct()
        )

    def clasificar_actividad(
        self,
        nombre_proceso: str,
        titulo_ventana: Optional[str]
    ) -> str:
        """Clasificar una actividad según proceso y título de ventana."""
        if nombre_proceso in self.CATEGORIAS['PROCESOS_TRABAJO_ESTUDIO']:
            return 'Trabajo/Estudio'

        if nombre_proceso in self.CATEGORIAS['NAVEGADORES']:
            if titulo_ventana:
                es_entretenimiento = any(
                    titulo.lower() in titulo_ventana.lower()
                    for titulo in self.CATEGORIAS['TITULOS_ENTRETENIMIENTO']
                )
                es_trabajo = any(
                    titulo.lower() in titulo_ventana.lower()
                    for titulo in self.CATEGORIAS['TITULOS_TRABAJO_ESTUDIO']
                )
                if es_entretenimiento and not es_trabajo:
                    return 'Entretenimiento'
            return 'Trabajo/Estudio'

        if (
            nombre_proceso in self.CATEGORIAS['PROCESOS_INACTIVOS'] or
            (nombre_proceso == 'explorer' and not titulo_ventana)
        ):
            return 'Inactividad'

        if nombre_proceso in self.CATEGORIAS['PROCESOS_ENTRETENIMIENTO']:
            return 'Entretenimiento'

        if nombre_proceso in self.CATEGORIAS['JUEGOS']:
            return 'Juegos'

        if nombre_proceso in self.CATEGORIAS['CONFIGURACIONES']:
            return 'Sistema/Configuración'

        return 'Otros'


class AnalizadorActividades:
    """Análisis y filtrado de actividades."""

    ELEMENTOS_POR_PAGINA = 10
    CHUNK_SIZE = 100
    TOP_PROCESOS = 6

    def __init__(self):
        self.clasificador = ClasificadorActividades()
        self._inicializar_categorias()

    @lru_cache(maxsize=1)
    def _inicializar_categorias(self) -> None:
        """Inicializa y cachea la lista de categorías."""
        self.categorias = list(
            Categoria.objects
            .exclude(nombre__in=['Otros', 'Navegación General'])
            .values_list('nombre', flat=True)
        )

    def _convertir_fecha_utc(self, fecha: str) -> datetime:
        """Convierte una fecha ISO a UTC."""
        return datetime.fromisoformat(fecha).astimezone(pytz.utc)

    def filtrar_actividades_por_fecha(
        self,
        actividades: QuerySet,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        fecha_exacta: Optional[str] = None
    ) -> QuerySet:
        """Filtra actividades por fecha."""
        try:
            if fecha_inicio and fecha_fin:
                return actividades.filter(
                    timestamp__range=[
                        self._convertir_fecha_utc(fecha_inicio),
                        self._convertir_fecha_utc(fecha_fin)
                    ]
                )

            fecha_referencia = (
                self._convertir_fecha_utc(fecha_exacta)
                if fecha_exacta
                else datetime.now()
            )
            return actividades.filter(timestamp__date=fecha_referencia.date())

        except (ValueError, TypeError) as e:
            logging.info("Error al filtrar las actividades por fecha %s", e)
            return actividades.none()

    def filtrar_actividades_por_usuario(
        self,
        actividades: QuerySet,
        nombre_usuario: Optional[str] = None,
    ) -> QuerySet:
        """Filtra actividades por usuario."""
        return (
            actividades.filter(usuario__iexact=nombre_usuario)
            if nombre_usuario
            else actividades
        )

    def filtrar_actividades_por_categoria(
        self,
        actividades: QuerySet,
        categoria: Optional[str] = None,
    ) -> QuerySet:
        """Filtra actividades por categoría."""
        if not categoria:
            return actividades

        actividades_pk = set()
        for actividad in actividades.iterator(chunk_size=self.CHUNK_SIZE):
            if self.clasificador.clasificar_actividad(
                actividad.nombre_proceso,
                actividad.titulo_ventana
            ) == categoria:
                actividades_pk.add(actividad.pk)

        return actividades.filter(pk__in=actividades_pk)

    def filtrar_actividades_por_consulta(
        self,
        actividades: QuerySet,
        consulta_busqueda: Optional[str] = None
    ) -> QuerySet:
        """Filtra actividades por texto."""
        if not consulta_busqueda:
            return actividades

        return actividades.filter(
            Q(nombre_proceso__icontains=consulta_busqueda) |
            Q(titulo_ventana__icontains=consulta_busqueda)
        )

    def obtener_desglose_tiempo_categorias(
        self,
        actividades: QuerySet,
        fecha_referencia: Optional[datetime] = None,
        categorias_excluidas: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Calcula desglose de tiempo por categoría"""
        categorias_excluidas = categorias_excluidas or []
        desglose_tiempo = {
            cat: 0.0 for cat in self.categorias
            if cat not in categorias_excluidas
        }

        for actividad in actividades.iterator(chunk_size=self.CHUNK_SIZE):
            categoria = self.clasificador.clasificar_actividad(
                actividad.nombre_proceso,
                actividad.titulo_ventana
            )
            if categoria in desglose_tiempo:
                desglose_tiempo[categoria] += float(
                    actividad.segundos_empleados
                )

        return desglose_tiempo

    def calcular_estadisticas_detalladas(
        self,
        actividades: QuerySet,
        consulta_busqueda: Optional[str] = None,
        pagina: int = 1
    ) -> Dict[str, Union[QuerySet, Dict]]:
        """Genera estadísticas."""

        procesos_principales = (
            actividades
            .values('nombre_proceso')
            .annotate(
                tiempo_total=Sum('segundos_empleados'),
            )
            .order_by('-tiempo_total')[:self.TOP_PROCESOS]
        )

        if consulta_busqueda:
            actividades = self.filtrar_actividades_por_consulta(
                actividades,
                consulta_busqueda
            )

        paginador = Paginator(
            actividades.order_by('-timestamp'),
            self.ELEMENTOS_POR_PAGINA
        )
        pagina_obj = paginador.get_page(pagina)

        return {
            'registros': pagina_obj,
            'procesos_principales': {
                'etiquetas': [
                    p['nombre_proceso'][:20] for p in procesos_principales
                ],
                'valores': [
                    float(p['tiempo_total'])/3600 for p in procesos_principales
                ]
            }
        }

    def obtener_tiempos_por_categoria_ultimos_7_dias(
        self,
        actividades: QuerySet,
        fecha_inicio: Optional[str] = None,
        fecha_exacta: Optional[str] = None
    ) -> Dict[str, Union[List[ChartData], List[str]]]:
        """Calcula tiempos por categoría para los últimos 7 días."""
        tiempos_por_categoria = {
            i: {cat: 0.0 for cat in self.categorias if cat != 'Inactividad'}
            for i in range(7)
        }

        fecha_dt = (
            self._convertir_fecha_utc(fecha_inicio or fecha_exacta)
            if (fecha_inicio or fecha_exacta)
            else datetime.now()
        )

        fecha_inicio_dt = (
            fecha_dt if fecha_inicio
            else (fecha_dt - timezone.timedelta(days=6))
        ).date()

        etiquetas_fechas = []
        for i in range(7):
            fecha = fecha_inicio_dt + timezone.timedelta(days=i)
            actividades_dia = actividades.filter(timestamp__date=fecha)

            for actividad in actividades_dia.iterator(
                chunk_size=self.CHUNK_SIZE
            ):
                categoria = self.clasificador.clasificar_actividad(
                    actividad.nombre_proceso,
                    actividad.titulo_ventana
                )
                if categoria in tiempos_por_categoria[i]:
                    tiempos_por_categoria[i][categoria] += float(
                        actividad.segundos_empleados
                    )

            etiquetas_fechas.append(fecha.strftime("%d/%m/%Y"))

        return {
            'categoria_dias_datasets': [
                {
                    'label': categoria,
                    'data': [
                        tiempos_por_categoria[i][categoria]/3600
                        for i in range(7)
                    ]
                }
                for categoria in self.categorias
                if categoria != 'Inactividad'
            ],
            'categoria_dias_etiquetas': etiquetas_fechas
        }

    def obtener_datos_por_hora(
        self,
        actividades: QuerySet
    ) -> Dict[str, Union[List[ChartData], List[str]]]:
        """Calcula datos de uso por hora."""
        datos_hora_categorias = {
            i: {cat: 0.0 for cat in self.categorias}
            for i in range(24)
        }

        for actividad in actividades.iterator(chunk_size=self.CHUNK_SIZE):
            categoria = self.clasificador.clasificar_actividad(
                actividad.nombre_proceso,
                actividad.titulo_ventana
            )
            if categoria in self.categorias:
                hora = timezone.localtime(actividad.timestamp).hour
                datos_hora_categorias[hora][categoria] += float(
                    actividad.segundos_empleados
                )

        return {
            'categorias_hora_datasets': [
                {
                    'label': categoria,
                    'data': [
                        datos_hora_categorias[h][categoria]/3600
                        if datos_hora_categorias[h][categoria] else 'null'
                        for h in range(24)
                    ]
                }
                for categoria in self.categorias
            ],
            'categorias_hora_etiquetas': [
                f"{str(h).zfill(2)}:00" for h in range(24)
            ]
        }

    def obtener_datos_categorias(
        self,
        actividades: QuerySet
    ) -> Dict[str, Union[str, List[CategoriaData], List[str], List[float]]]:
        """Calcula estadísticas de categorías."""
        desglose_tiempo = self.obtener_desglose_tiempo_categorias(
            actividades,
            categorias_excluidas=['Inactividad']
        )

        tiempo_total = sum(desglose_tiempo.values())

        if not tiempo_total:
            return {
                'tiempo_pantalla': "0",
                'top_categorias': [],
                'categorias_etiquetas': [],
                'categorias_valores': []
            }

        categorias_ordenadas = sorted(
            desglose_tiempo.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        desglose_completo = self.obtener_desglose_tiempo_categorias(
            actividades
        )
        porcentajes = {
            categoria: (tiempo / tiempo_total * 100)
            for categoria, tiempo in desglose_completo.items()
        }

        return {
            'tiempo_pantalla': str(tiempo_total).replace(",", "."),
            'top_categorias': [
                {
                    'categoria': cat,
                    'tiempo': tiempo,
                    'porcentaje': (tiempo / tiempo_total * 100)
                }
                for cat, tiempo in categorias_ordenadas
            ],
            'categorias_etiquetas': list(porcentajes.keys()),
            'categorias_valores': list(porcentajes.values()),
        }
