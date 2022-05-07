from flask import Blueprint

moderate_bp = Blueprint("moderate_bp", __name__)

from . import routes
