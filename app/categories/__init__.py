from flask import Blueprint

categories_bp = Blueprint('categories', __name__)

from app.categories import routes  # noqa: E402, F401
