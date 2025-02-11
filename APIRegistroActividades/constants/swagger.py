template = {
  "swagger": "2.0",
  "info": {
    "title": "API de registro de actividades del los usuarios",
    "description": "API para registrar las actividades de " +
                   "los usuarios en una base de datos",
    "contact": {
      "responsibleDeveloper": "Jefer Alexis Gonzalez Romero",
      "email": "jefer12543@gmail.com",
      "url": "https://github.com/AlexisGR117",
    },
    "termsOfService": "",
    "version": "0.0.1"
  },
  "basePath": "/",
  "schemes": [
    "http"
  ],
  "securityDefinitions": {
    "BasicAuth": {
        "type": "basic"
    }
  },
  "security": [{
    "BasicAuth": []
  }]
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}