from flask import Blueprint

income_bp = Blueprint('income', __name__, url_prefix='/income')

from app.income import routes
