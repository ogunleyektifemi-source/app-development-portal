from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )


class ProjectRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    project_type = db.Column(
        db.String(100),
        nullable=False
    )

    project_description = db.Column(
        db.Text,
        nullable=False
    )

    budget = db.Column(
        db.String(100)
    )

    status = db.Column(
        db.String(50),
        default="New"
    )

    rejection_reason = db.Column(
        db.Text
    )

    cancellation_reason = db.Column(
        db.Text
    )


class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project_request.id"),
        nullable=False
    )

    sender = db.Column(
        db.String(50),
        nullable=False
    )

    message_text = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Notification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project_request.id"),
        nullable=True
    )

    message = db.Column(
        db.String(255),
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class PasswordResetToken(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    token = db.Column(
        db.String(200),
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )


class ProjectFile(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project_request.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_by = db.Column(
        db.String(20),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )