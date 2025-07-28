from flask import Flask, request, jsonify
from extensions import db, mail
from config import *
from models import User, Purchase
from utils import send_verification_email, send_purchase_key_email, send_reset_password_email
import random

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    mail.init_app(app)

    @app.route('/register', methods=['POST'])
    def register():
        email = request.json['email']
        code = str(random.randint(100000, 999999))
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, verify_code=code)
            db.session.add(user)
        else:
            user.verify_code = code
        db.session.commit()
        send_verification_email(email, code)
        return jsonify({'message': 'Verification code sent'}), 201

    @app.route('/verify', methods=['POST'])
    def verify():
        email = request.json['email']
        code = request.json['code']
        user = User.query.filter_by(email=email).first()
        if user and user.verify_code == code:
            user.verified = True
            db.session.commit()
            return jsonify({'message': 'Email verified!'})
        return jsonify({'error': 'Invalid code'}), 400

    @app.route('/buy', methods=['POST'])
    def buy():
        email = request.json['email']
        key_entry = Purchase(user_email=email)
        db.session.add(key_entry)
        db.session.commit()
        send_purchase_key_email(email, key_entry.license_key)
        return jsonify({'message': 'License key sent', 'key': key_entry.license_key})

    @app.route('/reset-request', methods=['POST'])
    def reset_request():
        email = request.json['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'No such user'}), 404
        code = str(random.randint(100000, 999999))
        user.reset_code = code
        db.session.commit()
        send_reset_password_email(email, code)
        return jsonify({'message': 'Reset code sent'})

    @app.route('/reset-password', methods=['POST'])
    def reset_password():
        email = request.json['email']
        code = request.json['code']
        new_password = request.json['new_password']
        user = User.query.filter_by(email=email).first()
        if user and user.reset_code == code:
            # Здесь предполагается, что смену пароля нужно обработать отдельно в основной базе
            user.reset_code = None
            db.session.commit()
            return jsonify({'message': 'Password reset code accepted. Please update password in main service.'})
        return jsonify({'error': 'Invalid code'}), 400

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
