from extensions import db
import random
import string

def generate_license_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    verify_code = db.Column(db.String(6))
    reset_code = db.Column(db.String(6))

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    license_key = db.Column(db.String(32), default=generate_license_key)
