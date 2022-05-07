from random import randrange
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models.posts_model import Post
from app.models.users_model import User


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        user = User(
            username=fake.user_name(),
            name=fake.name(),
            email=fake.email(),
            confirmed=True,
            password="password",
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date(),
            last_seen=fake.past_date(),
            premium_account=fake.boolean(),
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        user = User.query.offset(randrange(0, user_count)).first()
        post = Post(
            title=fake.text(max_nb_chars=128),
            raw_body=fake.text(),
            timestamp=fake.past_date(),
            author=user,
        )
        db.session.add(post)
    db.session.commit()
