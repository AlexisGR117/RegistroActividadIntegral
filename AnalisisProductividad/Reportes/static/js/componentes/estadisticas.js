class GestorEstadisticas {
    constructor() {
        this.inicializarEstadisticas();
    }

    inicializarEstadisticas() {
        this.actualizarTiempoPantalla();
        this.actualizarTopCategorias();
    }

    actualizarTiempoPantalla() {
        const tiempoFormateado = FormateoTiempo.formatear(tiempo_pantalla);
        $('#horas').text(tiempoFormateado.horas);
        $('#minutos').text(tiempoFormateado.minutos.toString().padStart(2, '0'));
    }

    actualizarTopCategorias() {
        top_3_categorias.forEach((categoria, index) => {
            const categoriaEscapada = categoria.categoria.replace('/', '\\/');
            const $categoria = $(`#top-${categoriaEscapada}`);
            const $barra = $(`#top-${categoriaEscapada}-barra`);

            if ($categoria.length) {
                $categoria.text(FormateoTiempo.formatear(categoria.tiempo).formatoHorasMinutos);
            }

            if ($barra.length) {
                $barra.css({
                    width: `${categoria.porcentaje}%`,
                    backgroundColor: PALETA_COLORES.categorias[categoria.categoria]
                });
            }
        });
    }
}