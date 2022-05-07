from datetime import datetime
import bleach


from flask import url_for


from app import db
from app.exceptions import ValidationError
# Do not remove
from app.models.comments_model import Comment


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(128), nullable=False)
    image = db.Column(db.String(64), default="default_post_image.jpg")
    raw_body = db.Column(db.UnicodeText, nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["h1", "h2", "h3", "p", "pre", "div", "span", "big", "small", "tt", "code",
                        "kbd", "samp", "var", "del", "ins", "cite", "q", "strong", "b", "em", "i",
                        "u", "s", "ol", "ul", "li", "blockquote", "a", "img", "table", "caption",
                        "thead", "tbody", "tfoot", "tr", "th", "td", "hr", ]
        target.body = bleach.linkify(
            bleach.clean(
                value,
                tags=allowed_tags,
                strip=True,
            )
        )

    def to_json(self):
        json_post = {
            "url": url_for("api_v1_bp.get_post", id=self.id),
            "raw_body": self.raw_body,
            "body": self.body,
            "timestamp": self.timestamp,
            "author_url": url_for("api_v1_bp.get_user", id=self.author_id),
            "comments_url": url_for("api_v1_bp.get_post_comments", id=self.id),
            "comment_count": self.comments.count(),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        title = json_post.get("title")
        if title is None or title == "":
            raise ValidationError("Post does not have a title.")

        raw_body = json_post.get("raw_body")
        if raw_body is None or raw_body == "":
            raise ValidationError("Post does not have a raw_body.")

        return Post(title=title, raw_body=raw_body)

    def __repr__(self) -> str:
        return f"<Post id={self.id}, title={self.title}"


db.event.listen(Post.raw_body, "set", Post.on_changed_body)
