import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from constants.swagger import swagger_config, template
from .routes import registro_actividades_bp
from .utils import inicializar_bd
from .rotacionLogs import configuracion_logging


def create_app():
    app = Flask(__name__)

    log_file = os.getenv("LOG_FILE", "registro_actividades")
    logging = configuracion_logging(log_file)
    
    CORS(app)

    app.config['SWAGGER'] = {
        'title': 'API para registrar las actividades de ' +
                 'los usuarios en la base de datos',
        'uiversion': 3
    }
    Swagger(app, config=swagger_config, template=template)

    app.register_blueprint(registro_actividades_bp)
    inicializar_bd()
    logging.info("Aplicacion inicializada")
    return app
