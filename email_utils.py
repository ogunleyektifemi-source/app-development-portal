from threading import Thread
from flask_mail import Message

def _send(mail, app, subject, recipient, body):
    with app.app_context():
        msg = Message(
            subject=subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=[recipient]
        )
        msg.body = body
        mail.send(msg)

def send_email(mail, app, subject, recipient, body):
    Thread(
        target=_send,
        args=(mail, app, subject, recipient, body),
        daemon=True
    ).start()