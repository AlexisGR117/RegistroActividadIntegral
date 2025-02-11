import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from marshmallow import Schema, fields, ValidationError
from app.utils import registrar_actividades_usuario

registro_actividades_bp = Blueprint('registro_actividades', __name__)


class RegistroActividadSchema(Schema):
    timestamp = fields.Str(required=True)
    nombre_computador = fields.Str(required=True)
    usuario = fields.Str(required=True)
    titulo_ventana = fields.Str(required=True)
    nombre_proceso = fields.Str(required=True)
    pantalla = fields.Str(required=True)
    segundos_empleados = fields.Float(required=True)


schema = RegistroActividadSchema(many=True)


@registro_actividades_bp.route('/registro_actividades', methods=['POST'])
@swag_from('../constants/docs/registro_actividades.yaml')
def api_registro_actividades():
    datos = request.get_json()
    if not isinstance(datos, list):
        return jsonify({"error": "Se esperaba una lista de actividades"}), 400
    try:
        datos_validados = schema.load(datos)
    except ValidationError as e:
        return jsonify(
            {"error": "Datos incorrectos", "message": e.messages}
        ), 400
    try:
        registrar_actividades_usuario(datos_validados)
    except Exception as e:
        logging.error("Error en el registro de actividades: %s", e)
        return jsonify({"error": "Error al registrar las actividades"}), 500

    return jsonify({"message": "Registro exitoso"}), 200
