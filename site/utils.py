from flask import current_app, render_template
from flask_mail import Message
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

def send_verification_email(to, code):
    try:
        with current_app.app_context():
            msg = Message('Код подтверждения от LZT Marketplace', recipients=[to])
            msg.body = f'Здравствуйте!\n\nВаш код подтверждения: {code}\n\nВведите его на странице верификации.\n\nС уважением,\nLZT Marketplace'
            msg.html = render_template('email/verification.html', code=code)
            current_app.extensions['mail'].send(msg)
            logger.info(f"Письмо отправлено на {to} с кодом {code}")
    except Exception as e:
        logger.error(f"Ошибка отправки email на {to}: {str(e)}")
        raise

def send_purchase_key_email(to, license_key):
    try:
        with current_app.app_context():
            msg = Message('Ваш лицензионный ключ', recipients=[to])
            msg.body = f'Ваш ключ: {license_key}'
            msg.html = render_template('email/purchase_key.html', key=license_key)
            current_app.extensions['mail'].send(msg)  # Используем current_app.extensions['mail']
    except Exception as e:
        logger.error(f"Ошибка отправки ключа на {to}: {str(e)}")
        raise

def send_reset_password_email(to, code):
    try:
        with current_app.app_context():
            msg = Message('Код для сброса пароля', recipients=[to])
            msg.body = f'Код для сброса: {code}'
            msg.html = render_template('email/reset_password.html', code=code)
            current_app.extensions['mail'].send(msg)  # Используем current_app.extensions['mail']
    except Exception as e:
        logger.error(f"Ошибка отправки кода сброса на {to}: {str(e)}")
        raise
