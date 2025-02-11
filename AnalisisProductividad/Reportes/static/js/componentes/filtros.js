class GestorFiltros {
    constructor() {
        this.autoEnvio = true;
        this.inicializar();
    }

    inicializar() {
        this.inicializarSelect2();
        this.establecerFechasPorDefecto();
        this.configurarEventos();
    }

    inicializarSelect2() {
        $('#usuario').select2({
            placeholder: "Todos los usuarios",
            allowClear: true,
            width: '100%'
        }).on('change', () => {
            if (this.autoEnvio) {
                $('#filtros-form').submit();
            }
        });
    }

    establecerFechasPorDefecto() {
        const fechaActual = UtilidadesFecha.obtenerFechaActual();
        if (!$('#fecha-exacta, #fecha-inicio, #fecha-fin').filter((_, el) => el.value).length) {
            $('#fecha-exacta').val(fechaActual.fecha);
        }
    }

    configurarEventos() {
        this.configurarEventosFechas();
        this.configurarAutoEnvio();
    }

    configurarEventosFechas() {
        const $fechaExacta = $('#fecha-exacta');
        const $fechaInicio = $('#fecha-inicio');
        const $fechaFin = $('#fecha-fin');

        $fechaExacta.on('change', () => {
            this.autoEnvio = false;
            $fechaInicio.val('');
            $fechaFin.val('');
            this.autoEnvio = true;
            if (this.autoEnvio) $('#filtros-form').submit();
        });

        $fechaInicio.on('change', () => {
            this.autoEnvio = false;
            if ($fechaInicio.val() && !$fechaFin.val()) {
                $fechaFin.val(UtilidadesFecha.obtenerFechaActual().fechaHora);
            }
            $fechaExacta.val('');
            this.autoEnvio = true;
            if (this.autoEnvio) $('#filtros-form').submit();
        });

        $fechaFin.on('change', () => {
            this.autoEnvio = false;
            if ($fechaFin.val() && !$fechaInicio.val()) {
                $fechaInicio.val('2025-01-17T00:00');
            }
            $fechaExacta.val('');
            this.autoEnvio = true;
            if (this.autoEnvio) $('#filtros-form').submit();
        });
    }

    configurarAutoEnvio() {
        $('#categoria').on('change', () => {
            if (this.autoEnvio) $('#filtros-form').submit();
        });
    }
}