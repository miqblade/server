from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ludiflex_admin:joker1337@34.30.158.137:5432/ludiflex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'

db = SQLAlchemy(app)

class ActivationKey(db.Model):
    __tablename__ = 'activation_keys'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer)
    key = db.Column(db.String(64))
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    used = db.Column(db.Boolean)

class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    folder_path = db.Column(db.String(255))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image = db.Column(db.String(100))
    category = db.Column(db.String(50))

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    package_id = db.Column(db.Integer)
    key_id = db.Column(db.Integer)
    purchase_date = db.Column(db.DateTime)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    balance = db.Column(db.Float)

admin = Admin(app, name='Админка Ludiflex', template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Package, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Purchase, db.session))
admin.add_view(ModelView(ActivationKey, db.session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
