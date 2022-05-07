from flask import Blueprint

api_v1_bp = Blueprint("api_v1_bp", __name__)

from . import auth, comments, errors, posts, users
