from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

ROLES = ('admin', 'manager', 'employee', 'moderator', 'client')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Wedding')
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    shoot_date = db.Column(db.Date)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120))
    service_type = db.Column(db.String(100))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')


class Review(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    author = db.Column(
        db.String(100)
    )

    text = db.Column(
        db.Text
    )

    rating = db.Column(
        db.Integer
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    approved = db.Column(
        db.Boolean,
        default=False
    )


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def log_action(action):
    db.session.add(Log(action=action))
