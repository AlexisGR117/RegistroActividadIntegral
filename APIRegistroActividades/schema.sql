CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    nombre_computador TEXT NOT NULL,
    usuario TEXT NOT NULL,
    titulo_ventana TEXT,
    nombre_proceso TEXT NOT NULL,
    pantalla TEXT NOT NULL,
    segundos_empleados REAL NOT NULL
);