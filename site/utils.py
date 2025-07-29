from flask import current_app, render_template
from flask_mail import Message

def send_verification_email(to, code):
    with current_app.app_context():
        msg = Message('Код подтверждения от LZT Marketplace', recipients=[to])
        msg.body = f'Здравствуйте!\n\nВаш код подтверждения: {code}\n\nВведите его на странице верификации.\n\nС уважением,\nLZT Marketplace'
        msg.html = render_template('email/verification.html', code=code)
        current_app.extensions['mail'].send(msg)

def send_purchase_key_email(to, license_key):
    with current_app.app_context():
        msg = Message('Ваш лицензионный ключ', recipients=[to])
        msg.body = f'Ваш ключ: {license_key}'
        msg.html = render_template('email/purchase_key.html', key=license_key)
        current_app.extensions['mail'].send(msg)

def send_reset_password_email(to, code):
    with current_app.app_context():
        msg = Message('Код для сброса пароля', recipients=[to])
        msg.body = f'Код для сброса: {code}'
        msg.html = render_template('email/reset_password.html', code=code)
        current_app.extensions['mail'].send(msg)
