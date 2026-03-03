from flask import Blueprint
installments_bp = Blueprint('installments', __name__, url_prefix='/installments')
from app.installments import routes
