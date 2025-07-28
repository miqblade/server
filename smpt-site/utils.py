from flask_mail import Message
from extensions import mail
from flask import current_app

def send_verification_email(to, code):
    with current_app.app_context():
        msg = Message('Код подтверждения', recipients=[to])
        msg.body = f'Ваш код подтверждения: {code}'
        mail.send(msg)

def send_purchase_key_email(to, license_key):
    with current_app.app_context():
        msg = Message('Ваш лицензионный ключ', recipients=[to])
        msg.body = f'Ваш ключ: {license_key}'
        mail.send(msg)

def send_reset_password_email(to, code):
    with current_app.app_context():
        msg = Message('Код для сброса пароля', recipients=[to])
        msg.body = f'Код для сброса: {code}'
        mail.send(msg)
