from datetime import datetime
from time import time
import jwt

from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from app.models.follows_model import Follow
from app.models.roles_model import Role, Permission
# Do not remove (needed for relationship)
from app.models.comments_model import Comment
from app.models.posts_model import Post


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))

    profile_image = db.Column(db.String(64), default="default_profile_image.jpg")
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    premium_account = db.Column(db.Boolean, default=False, nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["EMB_ADMIN_EMAIL"]:
                self.role = Role.query.filter_by(name="Administrator").first()
                self.premium_account = True
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expires_in=3600):
        return jwt.encode(
            {"confirm": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def confirm(token):
        try:
            id = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )["confirm"]
        except:
            return None
        return User.query.get(id)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )["reset_password"]
        except:
            return None
        return User.query.get(id)

    def generate_change_email_token(self, new_email, expires_in=600):
        return jwt.encode(
            {"confirm": self.id, "new_email": new_email, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    def verify_change_email_token(self, token):
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = data["confirm"]
            new_email = data["new_email"]
        except:
            return False
        if user_id != self.id:
            return False

        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    def generate_auth_token(self, expires_in=3600):  # 1 hour
        return jwt.encode(
            {
                "confirm": self.id,
                "exp": time() + expires_in,
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_auth_token(token):
        try:
            user_id = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )["confirm"]
        except:
            return None
        return User.query.get(user_id)

    def to_json(self):
        json_user = {
            "url": url_for("api_v1_bp.get_user", id=self.id),
            "username": self.username,
            "member_since": self.member_since,
            "last_seen": self.last_seen,
            "posts_url": url_for("api_v1_bp.get_user_posts", id=self.id),
            "followed_posts_url": url_for("api_v1_bp.get_user_followed_posts", id=self.id),
            "post_count": self.posts.count(),
        }
        return json_user

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.id})>"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
