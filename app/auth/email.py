from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from .. import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['EMB_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['EMB_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', subject=subject, **kwargs)
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        to=user.email,
        subject="Reset Your Password",
        template="auth/email/reset_password_email",
        user=user,
        token=token,
    )


def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    send_email(
        to=user.email,
        subject="Welcome to EMB",
        template="auth/email/confirm_email",
        user=user,
        token=token,
    )
