from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User, db
import re

def simple_email_validator(form, field):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_pattern, field.data):
        raise ValidationError('Неверный формат email адреса')

def password_complexity(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать минимум 8 символов')
    if not re.search(r'\d', password):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Пароль должен содержать хотя бы один специальный символ')

class RegistrationForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.password.description = "Пароль должен содержать минимум 8 символов, цифры, заглавные и строчные буквы, специальные символы"

    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(min=4, max=50, message='Длина должна быть от 4 до 50 символов')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Это поле обязательно'), 
        simple_email_validator
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Это поле обязательно'),
        password_complexity
    ])
    
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Это поле обязательно'), 
        EqualTo('password', message='Пароли должны совпадать')
    ])
    
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Выберите другое.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже используется. Используйте другой email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Это поле обязательно')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Это поле обязательно')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
