#!/usr/bin/python
import sys

active_this = (
    "C:/Users/AlexisGR117/Desktop/RegistroActividadIntegral/"
    "APIRegistroActividades/VENV_API_REGISTRO_ACTIVIDADES/"
    "Scripts/activate_this.py"
)

with open(active_this, encoding='utf-8') as f:
    import runpy
    runpy.run_path(active_this, run_name="__main__")

from dotenv import load_dotenv

load_dotenv(
    "C:/Users/AlexisGR117/Desktop/RegistroActividadIntegral/"
    "APIRegistroActividades/.env"
)
sys.path.insert(
    0,
    "C:/Users/AlexisGR117/Desktop/RegistroActividadIntegral/APIRegistroActividades"
)

from run import app as application
