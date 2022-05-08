from flask import current_app, render_template
from flask_login import login_required
from flask_sqlalchemy import get_debug_queries

from app.decorators import admin_required

from . import main_bp


@main_bp.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['EMB_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                f'Slow query: {query.statement}\nParameters: {query.parameters}\nDuration: {query.duration}s\nContext: {query.context}\n')
    return response


@main_bp.route("/")
@main_bp.route("/home/")
def home():
    return render_template("main/home.html")


@ main_bp.route("/pricing/")
def pricing():
    return render_template("main/pricing.html")


@ main_bp.route("/about/")
def about():
    return render_template("main/about.html")
