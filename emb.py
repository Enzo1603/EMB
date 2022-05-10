import os
from datetime import datetime

from flask_migrate import Migrate
from app import create_app, db, cli
from app.models.roles_model import Permission, Role
from app.models.follows_model import Follow
from app.models.users_model import User
from app.models.posts_model import Post
from app.models.comments_model import Comment


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
cli.register(app)


@app.context_processor
def inject_now():
    return {"utcnow": datetime.utcnow()}


@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Follow=Follow, Role=Role, Permission=Permission, Post=Post, Comment=Comment)
