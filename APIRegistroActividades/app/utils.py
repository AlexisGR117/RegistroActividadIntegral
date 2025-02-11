import os
from psycopg2 import pool, extras
import logging

db_pool = pool.SimpleConnectionPool(
    minconn=5,
    maxconn=30,
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'actividades_usuarios'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres')
)


class ConexionBaseDatos:
    def __enter__(self):
        self.conexion = db_pool.getconn()
        if not self.conexion:
            raise ConnectionError(
                "No se pudo obtener una conexión a la base de datos."
            )
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conexion:
            db_pool.putconn(self.conexion)


def obtener_conexion_bd():
    return ConexionBaseDatos()


def inicializar_bd():
    try:
        with obtener_conexion_bd() as conexion:
            with conexion.cursor() as cur:
                schema_path = os.path.join(
                    os.path.dirname(__file__), "../schema.sql"
                )
                with open(
                    schema_path, 'r', encoding='utf-8'
                ) as archivo_esquema:
                    cur.execute(archivo_esquema.read())
                conexion.commit()
    except Exception as e:
        if conexion:
            conexion.rollback()
        logging.error(f"Error al inicializar la base de datos: {e}")
        raise


def registrar_actividades_usuario(datos):
    query = """
        INSERT INTO actividades (
            timestamp, nombre_computador, usuario, 
            titulo_ventana, nombre_proceso, pantalla, segundos_empleados
        ) VALUES %s
    """
    values = [
        (
            item['timestamp'], item['nombre_computador'], item['usuario'],
            item['titulo_ventana'], item['nombre_proceso'],
            item['pantalla'], item['segundos_empleados']
        ) for item in datos
    ]
    try:
        with obtener_conexion_bd() as conexion:
            with conexion.cursor() as cur:
                extras.execute_values(cur, query, values)
                conexion.commit()
    except Exception as e:
        if conexion:
            conexion.rollback()
        logging.error(f"Error al registrar actividades: {e}")
        raise
