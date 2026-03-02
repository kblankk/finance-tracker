"""WSGI entry point for PythonAnywhere deployment."""
from dotenv import load_dotenv
import os

project_home = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_home, '.env'))

from app import create_app

application = create_app('config.ProductionConfig')
