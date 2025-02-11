class FormateoTiempo {
    static formatear(segundos) {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        const segundosRestantes = Math.floor((((segundos / 3600) % 1) * 60) % 1 * 60);
        
        return {
            horas,
            minutos,
            segundos: segundosRestantes,
            formatoHorasMinutos: `${horas}h ${minutos.toString().padStart(2, '0')}m`,
            formatoCompleto: `${horas}:${minutos.toString().padStart(2, '0')}:${segundosRestantes.toString().padStart(2, '0')}`
        };
    }
}