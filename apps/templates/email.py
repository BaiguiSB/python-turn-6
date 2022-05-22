from . import mail
from flask_mail import Message
from flask import current_app


def send_check_main(address, token):
    with current_app.app_context():
        msg = Message(subject="confirm", sender=current_app.config['MAIL_USERNAME'], recipients=[address])
        msg.body = "/api/v1/user/confirm/" + token
        mail.send(msg)
