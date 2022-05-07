from datetime import datetime

import bleach

from app import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    raw_body = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["strong", "b", "em", "i", "ol", "ul", "li", "a", ]
        target.body = bleach.linkify(
            bleach.clean(
                value,
                tags=allowed_tags,
                strip=True,
            )
        )


db.event.listen(Comment.raw_body, "set", Comment.on_changed_body)
