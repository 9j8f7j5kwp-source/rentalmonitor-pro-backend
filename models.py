from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RentalObject(db.Model):
    __tablename__ = 'rental_objects'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    area = db.Column(db.Float, nullable=False)
    is_for_sale = db.Column(db.Boolean, default=False)
    price_total = db.Column(db.Float)
    rent_per_sqm = db.Column(db.Float)
    profitability = db.Column(db.Float, default=0.0)
    is_undervalued = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
