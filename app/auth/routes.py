from datetime import timedelta

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import auth_bp
from app.auth.forms import ChangeEmailForm, ChangePasswordForm, RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from app.auth.email import send_change_email_email, send_password_reset_email, send_confirmation_email
from app.models.users_model import User


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != "auth_bp" \
                and request.endpoint != "static":
            return redirect(url_for("auth_bp.unconfirmed"))


@auth_bp.route("/unconfirmed/")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("user_bp.profile", username=current_user.username))
    return render_template("auth/unconfirmed.html")


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You already have an account")
        return redirect(url_for("user_bp.profile", username=current_user.username))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        flash("A confirmation email has been sent to your email address.")
        return redirect(url_for("auth_bp.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/confirm/<string:token>/")
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("Your account has already been confirmed.")
        return redirect(url_for("user_bp.profile", username=current_user.username))
    user = User.confirm(token)
    if not user:
        flash("The confirmation link is invalid or has expired.")
    else:
        user.confirmed = True
        db.session.commit()
        flash("You have confirmed your account. Thank You!")
    return redirect(url_for("user_bp.profile", username=current_user.username))


@auth_bp.route("/confirm/")
@login_required
def resend_confirmation():
    send_confirmation_email(current_user)
    flash("A new confirmation email has been sent to your email address.")
    return redirect(url_for("auth_bp.login"))


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("user_bp.profile", username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.verify_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth_bp.login"))

        login_user(user, form.remember_me.data, duration=timedelta(days=180))
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("user_bp.profile", username=current_user.username)
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/reset_password_request/", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        flash("""You are already logged in. Please you use "Change Password" in the top right corner.""")
        return redirect(url_for("user_bp.profile", username=current_user.username))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash("Check your email for the instructions to reset your password.")
            return redirect(url_for("auth_bp.login"))
        flash("Email does not exist.")

    return render_template("auth/reset_password_request.html", form=form)


@auth_bp.route("/reset_password/<string:token>/", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.home"))
    user = User.verify_reset_password_token(token)
    if not user:
        flash("Reset token is invalid. You need to request a new one.")
        return redirect(url_for("main_bp.home"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.commit()
        flash("Your password has been reset.")
        return redirect(url_for("auth_bp.login"))
    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/change-password/", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("user_bp.profile", username=current_user.username))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html", form=form)


@auth_bp.route("/change-email/", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.new_email.data.lower()
            send_change_email_email(current_user, new_email)
            flash("An email with instructions to confirm your new email address has been sent to you.")
            return redirect(url_for('user_bp.profile', username=current_user.username))
        else:
            flash("Invalid email or password.")
    return render_template("auth/change_email.html", form=form)


@auth_bp.route('/change_email/<token>/')
@login_required
def change_email(token):
    if current_user.verify_change_email_token(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('user_bp.profile', username=current_user.username))


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main_bp.home"))
