from flask import Blueprint

payment_bp = Blueprint("payment_bp", __name__)

from . import routes
