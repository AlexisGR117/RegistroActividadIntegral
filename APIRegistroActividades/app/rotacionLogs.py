import logging
import os

from logging.handlers import RotatingFileHandler

MAX_PESO = 50 * 1024 * 1024  # 50 MB
CANT_ARCHIVOS_RESPALDO = 5
FORMATO_LOG = (
    "[%(asctime)s] {%(pathname)s:%(lineno)d}"
    "%(levelname)s - %(message)s"
)
NIVEL_LOGGING = logging.INFO


def configuracion_logging(nombre_aplicacion):
    try:
        logger = logging.getLogger()
        logger.setLevel(NIVEL_LOGGING)

        handler = RotatingFileHandler(
            os.path.join(
                os.path.dirname(__file__),
                f"../logs/{nombre_aplicacion}.log"
            ),
            maxBytes=MAX_PESO,
            backupCount=CANT_ARCHIVOS_RESPALDO
        )

        handler.setFormatter(logging.Formatter(FORMATO_LOG))

        logger.addHandler(handler)

        return logger
    except Exception as e:
        print(f"Error en configuracion de logs: {e}")
