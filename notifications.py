from flask import jsonify, redirect, url_for
from flask_login import login_required, current_user

from app import app
from models import db, Notification


