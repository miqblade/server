from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, redirect, url_for, flash, request, session
from models import db, User, Product, Package, ActivationKey, Purchase
from forms import RegistrationForm, LoginForm
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail
from flask import json
import os
import random
import string
import logging

from utils import send_purchase_key_email, send_reset_password_email, send_verification_email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ludiflex_admin:joker1337@34.28.211.167:5432/ludiflex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'mail.privateemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'support@lzt.store'
app.config['MAIL_PASSWORD'] = 't9#Ypn97DeZa.h-'
app.config['MAIL_DEFAULT_SENDER'] = 'support@lzt.store'

db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page"
login_manager.login_message_category = "error"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_country_emoji(country_code):
    """Возвращает emoji флага для кода страны"""
    emoji_map = {
        'US': '🇺🇸', 'RU': '🇷🇺', 'GB': '🇬🇧', 'DE': '🇩🇪',
        'FR': '🇫🇷', 'JP': '🇯🇵', 'CN': '🇨🇳', 'IN': '🇮🇳',
        'BR': '🇧🇷', 'CA': '🇨🇦', 'AU': '🇦🇺', 'KR': '🇰🇷',
        'UA': '🇺🇦', 'KZ': '🇰🇿', 'BY': '🇧🇾', 'TR': '🇹🇷',
        'IT': '🇮🇹', 'ES': '🇪🇸', 'PL': '🇵🇱', 'NL': '🇳🇱'
    }
    return emoji_map.get(country_code.upper(), '🌐')

@app.context_processor
def utility_processor():
    return dict(get_country_emoji=get_country_emoji)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def generate_activation_key():
    while True:
        chars = ''.join(random.choices(string.ascii_uppercase, k=16))
        key = '-'.join([chars[i:i+4] for i in range(0, 16, 4)])
        if not ActivationKey.query.filter_by(key=key).first():
            return key

def initialize_database():
    with app.app_context():
        try:
            db.create_all()
            create_test_data()
        except Exception as e:
            logger.critical(f"Database initialization failed: {e}")

def create_test_data():
    try:
        if Package.query.count() == 0:
            packages = [
                Package(id=1, name="Premium Monthly Subscription",
                        description="Full access to all templates and features",
                        price=29.99, folder_path="/premium", duration_days=30),
                
                Package(id=2, name="Basic Monthly Subscription",
                        description="Access to basic templates and features",
                        price=9.99, folder_path="/basic", duration_days=30),
                
                Package(id=3, name="Annual Subscription",
                        description="Full access for 1 year with 20% discount",
                        price=249.99, folder_path="/premium", duration_days=365)
            ]
            db.session.add_all(packages)
            db.session.commit()
            logger.info("Created test packages")

        if Product.query.count() == 0:
            products = [
                Product(name="LZT Motion Pack Vol.1",
                        description="Professional motion graphics pack for After Effects with 50+ presets",
                        price=49.99, image="product-1.png", package_id=1),
                
                Product(name="LZT Transitions Pro",
                        description="100+ smooth transitions for your video projects",
                        price=29.99, image="product-2.png", package_id=2),
                
                Product(name="LZT Text Animations",
                        description="200+ text animation presets for After Effects",
                        price=39.99, image="product-3.png", package_id=3),
                
                Product(name="LZT Particles Universe",
                        description="Create stunning particle effects with 30+ presets",
                        price=59.99, image="product-4.png", package_id=4)
            ]
            db.session.add_all(products)
            db.session.commit()
            logger.info("Created test products")

    except Exception as e:
        logger.error(f"Failed to create test data: {e}")
        db.session.rollback()

@app.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint in ['profile', 'cart']:
        flash("Please log in to access this page", "error")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('index.html')

@app.route('/resend-verification', methods=['GET'])
def resend_verification():
    email = session.get('email')
    if not email:
        flash('Session expired. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(email=email).first()
    if user:
        code = str(random.randint(100000, 999999))
        user.verify_code = code
        db.session.commit()
        try:
            send_verification_email(email, code)
            flash('A new verification code has been sent to your email.', 'success')
        except Exception as e:
            flash(f'Ошибка отправки кода: {str(e)}', 'danger')
    else:
        flash('User not found. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    return redirect(url_for('verify'))

@app.route('/reset-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            code = str(random.randint(100000, 999999))
            user.reset_code = code
            db.session.commit()
            session['email'] = email  # Сохраняем email в сессии
            try:
                send_reset_password_email(email, code)
                flash('The password reset code has been sent to your email.', 'success')
                return redirect(url_for('reset_password'))
            except Exception as e:
                flash(f'Error sending code: {str(e)}', 'danger')
        else:
            flash('Email not found.', 'danger')
    
    return render_template('reset_request.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    email = session.get('email')  # Получаем email из сессии
    if not email:
        flash('Session expired. Please request password reset again.', 'danger')
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.reset_code == code:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.reset_code = None
            db.session.commit()
            session.pop('email', None)  # Удаляем email из сессии
            flash('Password successfully changed! You can now log in.', 'success')
            return redirect(url_for('login'))
        flash('Invalid password reset code', 'danger')
    
    return render_template('reset_password.html', email=email)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
@login_required
def products():
    products = Product.query.all()
    cart_count = sum(session.get('cart', {}).values())
    return render_template('store.html', products=products, cart_count=cart_count)

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            code = str(random.randint(100000, 999999))
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                verify_code=code
            )
            db.session.add(user)
            db.session.commit()
            session['email'] = form.email.data  # Сохраняем email в сессии
            send_verification_email(form.email.data, code)
            flash('Registration successful! Verification code sent to your email.', 'success')
            return redirect(url_for('verify'))
        except IntegrityError as e:
            db.session.rollback()
            if "user_username_key" in str(e):
                form.username.errors.append('This username is already taken')
            elif "user_email_key" in str(e):
                form.email.errors.append('This email is already in use')
            else:
                flash('Error during registration', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if not user.verified:
                flash('Please verify your email before logging in.', 'error')
                return redirect(url_for('verify'))
            if user.password.startswith('$2b$'):
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    return redirect(request.args.get('next') or url_for('index'))
            elif user.password == form.password.data:
                user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                return redirect(request.args.get('next') or url_for('index'))
        
        flash('Incorrect email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    email = session.get('email')  # Получаем email из сессии
    if not email:
        flash('Session expired. Please register again.', 'danger')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        user = User.query.filter_by(email=email).first()
        if user and user.verify_code == code:
            user.verified = True
            user.verify_code = None
            db.session.commit()
            session.pop('email', None)  # Удаляем email из сессии после верификации
            flash('Email successfully verified! Now you can log in.', 'success')
            return redirect(url_for('login'))
        flash('Invalid verification code', 'danger')
    
    return render_template('verify.html', email=email)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    session['cart'] = cart
    flash('Product added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
        else:
            del cart[product_id_str]
        
        session['cart'] = cart
        flash('The product has been removed from the cart!', 'success')
    
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total
            })
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        selected_geos = json.loads(request.form.get('selected_geos', '[]'))
        if not selected_geos:
            flash('Please select at least one country', 'error')
            return redirect(url_for('cart'))
        
        cart = session.get('cart', {})
        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('cart'))
        
        product_id = next(iter(cart))
        product = Product.query.get(int(product_id))
        if not product:
            flash('Invalid item in cart', 'error')
            return redirect(url_for('cart'))
        
        package = product.package
        
        total = sum(Product.query.get(int(id)).price * qty for id, qty in cart.items())
        
        if current_user.balance < total:
            flash('Insufficient funds', 'error')
            return redirect(url_for('cart'))
        
        current_user.balance -= total
        
        key_str = generate_activation_key()
        expires_at = datetime.utcnow() + timedelta(days=package.duration_days)
        
        activation_key = ActivationKey(
            package_id=package.id,
            key=key_str,
            user_id=current_user.id,
            geo=json.dumps(selected_geos),
            expires_at=expires_at
        )
        db.session.add(activation_key)
        db.session.flush()
        
        purchase = Purchase(
            user_id=current_user.id,
            package_id=package.id,
            key_id=activation_key.id,
            purchase_date=datetime.utcnow()
        )
        db.session.add(purchase)
        
        db.session.commit()
        
        send_purchase_key_email(current_user.email, key_str)
        
        session.pop('cart', None)
        
        return render_template('purchase_success.html', 
                           activation_key={
                               'key': key_str,
                               'package': package,
                               'expires_at': expires_at,
                               'geo': selected_geos
                           })
    
    except Exception as e:
        db.session.rollback()
        flash('Error while placing your purchase: ' + str(e), 'error')
        return redirect(url_for('cart'))

@app.route('/profile')
@login_required
def profile():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return render_template('profile.html', user=current_user, now=now)

@app.route('/add_funds', methods=['POST'])
@login_required
def add_funds():
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Incorrect top-up amount', 'danger')
            return redirect(url_for('profile'))
        
        current_user.balance += amount
        db.session.commit()
        flash(f'The account has been successfully replenished by ${amount:.2f}', 'success')
    except ValueError:
        flash('Invalid amount format', 'danger')
    
    return redirect(url_for('profile'))

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
