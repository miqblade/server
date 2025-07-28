from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import desc

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    verified = db.Column(db.Boolean, default=False)  # Для верификации
    verify_code = db.Column(db.String(6))  # Код верификации
    reset_code = db.Column(db.String(6))  # Код сброса пароля
    activation_keys = db.relationship('ActivationKey', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='user', lazy='dynamic')

    def get_purchases(self):
        return self.purchases.order_by(desc(Purchase.purchase_date)).all()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), default='default.jpg')
    category = db.Column(db.String(50), default='After Effects')
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    package = db.relationship('Package', backref='products')

class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    folder_path = db.Column(db.String(255))
    duration_days = db.Column(db.Integer, default=30)

class ActivationKey(db.Model):
    __tablename__ = 'activation_key'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    geo = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    package = db.relationship('Package', backref='activation_keys')

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    key_id = db.Column(db.Integer, db.ForeignKey('activation_key.id'), nullable=False)  # Убедитесь что nullable=False
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    activation_key = db.relationship('ActivationKey', backref='purchase')
    package = db.relationship('Package', backref='purchases')
