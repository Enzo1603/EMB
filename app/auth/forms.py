from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp
from ..models.users_model import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(4, 32),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
               "Usernames must have only letters, numbers, dots or underscores."),
    ])
    email = StringField("Email Address", validators=[
                        DataRequired(), Email(), Length(6, 64)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
            Length(min=8),
        ]
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    terms_of_service = BooleanField("I accept the Terms of Service", validators=[DataRequired()])
    submit = SubmitField("Register")

    # pattern required!
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me", validators=[Optional()])
    submit = SubmitField("Log In")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
            Length(min=8),
        ]
    )
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Request Password Reset")
