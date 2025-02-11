class UtilidadesFecha {
    static obtenerFechaActual() {
        const hoy = new Date();
        const fecha = hoy.toISOString().split('T')[0];
        return {
            fecha,
            fechaHora: `${fecha}T23:59`
        };
    }
}