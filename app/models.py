from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)

    # backref='user' will be created from Reservation model

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))
    address = db.Column(db.String(150))
    pin_code = db.Column(db.String(10))
    price_per_hour = db.Column(db.Float)
    total_spots = db.Column(db.Integer)

    spots = db.relationship('ParkingSpot', backref='lot')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied

    # backref='reservations' will be created from Reservation model

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False)
    leave_time = db.Column(db.DateTime)
    cost = db.Column(db.Float)

    spot = db.relationship('ParkingSpot', backref='reservations')
    user = db.relationship('User', backref='reservations')

def create_default_admin():
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('admin', method='pbkdf2:sha256')
        admin = User(username='admin', password=hashed_pw, is_admin=True)
        db.session.add(admin)
        db.session.commit()
