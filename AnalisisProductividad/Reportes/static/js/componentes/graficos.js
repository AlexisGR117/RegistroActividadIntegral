class GestorGraficos {
    constructor() {
        this.inicializarGraficos();
    }

    inicializarGraficos() {
        this.crearGraficoRadar();
        this.crearGraficoProcesos();
        this.crearGraficoLineas();
        this.crearGraficoDias();
    }

    crearGraficoRadar() {
        const datosRadar = {
            labels: radar_etiquetas,
            datasets: [{
                label: 'Distribución de tiempo (%)',
                data: radar_valores,
                backgroundColor: PALETA_COLORES.principal.transparente,
                borderColor: PALETA_COLORES.principal.base,
                pointBackgroundColor: PALETA_COLORES.principal.base,
                pointHoverBorderColor: PALETA_COLORES.principal.base,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff'
            }]
        };

        new Chart($('#radar-actividad'), {
            type: 'radar',
            data: datosRadar,
            options: {
                ...this.obtenerConfiguracionBase(),
                elements: {
                    line: { borderWidth: 3 }
                },
                scales: {
                    r: {
                        angleLines: { display: true },
                        suggestedMin: 0,
                        suggestedMax: 60
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución de Tiempo de Actividades (%)'
                    }
                }
            }
        });
    }

    crearGraficoProcesos() {
        const datosProcesos = {
            labels: barras_procesos_etiquetas,
            datasets: [{
                data: barras_procesos_valores,
                backgroundColor: Object.values(PALETA_COLORES.categorias)
            }]
        };

        new Chart($('#bar-procesos'), {
            type: 'doughnut',
            data: datosProcesos,
            options: {
                ...this.obtenerConfiguracionBase(),
                plugins: {
                    title: {
                        display: true,
                        text: 'Procesos que Consumen Más Tiempo'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const tiempo = FormateoTiempo.formatear(context.parsed * 3600);
                                return tiempo.formatoCompleto;
                            }
                        }
                    }
                }
            }
        });
    }

    crearGraficoLineas() {
        const datasetsLineasProcesadas = lineas_datasets.map(dataset => ({
            ...dataset,
            backgroundColor: PALETA_COLORES.categorias[dataset.label],
            borderColor: PALETA_COLORES.categorias[dataset.label],
            tension: 0,
            fill: false,
            spanGaps: false
        }));

        new Chart($('#line-categorias'), {
            type: 'line',
            data: {
                labels: lineas_etiquetas,
                datasets: datasetsLineasProcesadas
            },
            options: {
                ...this.obtenerConfiguracionBase(),
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Hora del día'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Horas'
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    ...this.obtenerConfiguracionBase().plugins,
                    title: {
                        display: true,
                        text: 'Distribución durante el día'
                    }
                }
            }
        });
    }

    crearGraficoDias() {
        const datasetsDiasProcesados = barras_dias_datasets.map(dataset => ({
            ...dataset,
            backgroundColor: PALETA_COLORES.categorias[dataset.label]
        }));

        new Chart($('#bar-dias'), {
            type: 'bar',
            data: {
                labels: barras_dias_etiquetas,
                datasets: datasetsDiasProcesados
            },
            options: {
                ...this.obtenerConfiguracionBase(),
                plugins: {
                    ...this.obtenerConfiguracionBase().plugins,
                    title: {
                        display: true,
                        text: 'Tiempo en pantalla'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Días'
                        },
                        stacked: true
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Horas'
                        },
                        beginAtZero: true,
                        stacked: true
                    }
                }
            }
        });
    }

    obtenerConfiguracionBase() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: this.formatearEtiquetaTooltip.bind(this)
                    }
                }
            }
        };
    }

    formatearEtiquetaTooltip(context) {
        const tiempo = FormateoTiempo.formatear(context.parsed.y * 3600);
        return `${context.dataset.label}: ${tiempo.formatoCompleto}`;
    }
}