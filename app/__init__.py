import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
import os.path as op
from flask import Flask, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.form import SecureForm
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

admin = Admin(name='EMB Admin', template_mode='bootstrap4')


class MyModelView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth_bp.login"))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth_bp.login"))


bootstrap = Bootstrap5()

ckeditor = CKEditor()

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"

mail = Mail()

moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    admin.init_app(app, index_view=MyAdminIndexView())
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    if app.config["SSL_REDIRECT"]:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from app.models.comments_model import Comment
    from app.models.follows_model import Follow
    from app.models.posts_model import Post
    from app.models.roles_model import Role
    from app.models.users_model import User
    path = op.join(op.dirname(__file__), "static")
    admin.add_views(
        MyModelView(Comment, db.session, name="Comments"),
        MyModelView(Follow, db.session),
        MyModelView(Post, db.session),
        MyModelView(Role, db.session),
        MyModelView(User, db.session),
        FileAdmin(path, "/static/", name="Static Files")
    )

    from .api_v1 import api_v1_bp as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix="/api/v1")

    from .auth import auth_bp as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main_bp as main_blueprint
    app.register_blueprint(main_blueprint)

    from .moderate import moderate_bp as moderate_blueprint
    app.register_blueprint(moderate_blueprint, url_prefix="/moderate")

    from .payment import payment_bp as payment_blueprint
    app.register_blueprint(payment_blueprint, url_prefix="/payment")

    from .post import post_bp as post_blueprint
    app.register_blueprint(post_blueprint, url_prefix="/post")

    from .user import user_bp as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix="/user")

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app
