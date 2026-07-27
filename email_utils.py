from flask_mail import Message as MailMessage


def send_email(mail, app, subject, recipient, body):

    try:

        msg = MailMessage(
            subject=subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=[recipient]
        )

        msg.body = body

        mail.send(msg)

        print(f"Email sent to {recipient}")

    except Exception as e:

        print("EMAIL ERROR")
        print(e)