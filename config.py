import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "YOUR_SECRET_KEY_HERE"
    )

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:

        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )

    else:

        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" +
            os.path.join(
                BASE_DIR,
                "app_requests.db"
            )
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Mail Configuration

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