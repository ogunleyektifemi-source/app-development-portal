import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = "YOUR_SECRET_KEY_HERE"

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(
            BASE_DIR,
            "app_requests.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Mail Configuration

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "YOUR_EMAIL@gmail.com"
    MAIL_PASSWORD = "YOUR_APP_PASSWORD"


    # Uploads

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "png",
        "jpg",
        "jpeg",
        "zip"
    }