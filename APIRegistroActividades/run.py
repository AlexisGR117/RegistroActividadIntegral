from dotenv import load_dotenv
import logging
import traceback
from flask import Flask, jsonify
from app import create_app

load_dotenv()

app = create_app()


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error("Error interno: %s\n%s", e, traceback.format_exc())
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=False, port=8890)
