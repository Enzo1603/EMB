from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp
from wtforms.validators import ValidationError

from app.models.roles_model import Role
from app.models.users_model import User


class EditProfileForm(FlaskForm):
    name = StringField("Your Real Name", validators=[Length(0, 64)])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(4, 32),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
               "Usernames must have only letters, numbers, dots or underscores."),
    ])
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Update")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class EditProfileAdminForm(FlaskForm):
    name = StringField("Your Real Name", validators=[Length(0, 64)])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(4, 32),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
               "Usernames must have only letters, numbers, dots or underscores."),
    ])
    email = StringField("Email", validators=[DataRequired(), Length(6, 64), Email()])
    confirmed = BooleanField("Confirmed")
    new_password = PasswordField(
        "New Password",
        validators=[
            Length(min=8),
            EqualTo("confirm_new_password", message="Passwords must match."),
            Optional(),
        ]
    )
    confirm_new_password = PasswordField("Confirm New Password", validators=[Optional()])
    role = SelectField("Role", coerce=int)
    location = StringField("Location", validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Update")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeProfileImageForm(FlaskForm):
    new_profile_image = FileField("Change Profile Image", validators=[
                                  Optional(), FileAllowed(["jpg", "png"])])
    reset_profile_image = BooleanField("Reset Profile Image", validators=[Optional()])
    submit = SubmitField("Change Profile Image")
