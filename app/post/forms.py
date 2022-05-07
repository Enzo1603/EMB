from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class CommentForm(FlaskForm):
    raw_body = CKEditorField("", validators=[DataRequired(), Length(max=144)])
    submit = SubmitField("Submit Comment")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=128)])
    raw_body = CKEditorField("Post Body", validators=[DataRequired()])
    image = FileField(
        "Upload Post Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpe", "jpeg", "png", "gif", "svg", "bmp"]),
        ]
    )
    submit = SubmitField("Upload Post")
