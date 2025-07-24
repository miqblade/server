from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm
from models import db, User, Product, Package, ActivationKey, Purchase
import os
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ludiflex_admin:joker1337@34.30.158.137/ludiflex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
                        price=29.99, image="product-2.png", package_id=1),
                
                Product(name="LZT Text Animations",
                        description="200+ text animation presets for After Effects",
                        price=39.99, image="product-3.png", package_id=2),
                
                Product(name="LZT Particles Universe",
                        description="Create stunning particle effects with 30+ presets",
                        price=59.99, image="product-4.png", package_id=1)
            ]
            db.session.add_all(products)
            db.session.commit()
            logger.info("Created test products")

    except Exception as e:
        logger.error(f"Failed to create test data: {e}")
        db.session.rollback()

@app.route('/')
def index():
    if current_user.is_authenticated:
        products = Product.query.all()
        cart_count = sum(session.get('cart', {}).values())
        return render_template('store.html', products=products, cart_count=cart_count)
    return render_template('index.html')

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
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except IntegrityError as e:
            db.session.rollback()
            if "user_username_key" in str(e):
                form.username.errors.append('Это имя пользователя уже занято')
            elif "user_email_key" in str(e):
                form.email.errors.append('Этот email уже используется')
            else:
                flash('Произошла ошибка при регистрации', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password.startswith('$2b$'):
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    return redirect(request.args.get('next') or url_for('index'))
            elif user.password == form.password.data:
                user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                return redirect(request.args.get('next') or url_for('index'))
        
        flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)

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
    flash('Товар добавлен в корзину!', 'success')
    return redirect(url_for('index'))

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
        flash('Товар удалён из корзины!', 'success')
    
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
    cart = session.get('cart', {})
    if not cart:
        flash('Ваша корзина пуста', 'danger')
        return redirect(url_for('cart'))
    
    total = 0
    cart_items = []
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'package': product.package
            })
    
    if current_user.balance < total:
        flash('Недостаточно средств на балансе', 'danger')
        return redirect(url_for('cart'))
    
    current_user.balance -= total
    db.session.commit()
    
    activation_keys = []
    for item in cart_items:
        package = item['package']
        for _ in range(item['quantity']):
            key_str = generate_activation_key()
            expires_at = datetime.utcnow() + timedelta(days=package.duration_days)
            
            activation_key = ActivationKey(
                package_id=package.id,
                key=key_str,
                user_id=current_user.id,
                expires_at=expires_at
            )
            db.session.add(activation_key)
            db.session.flush()
            
            purchase = Purchase(
                user_id=current_user.id,
                package_id=package.id,
                key_id=activation_key.id
            )
            db.session.add(purchase)
            
            activation_keys.append({
                'key': key_str,
                'package': package,
                'expires_at': expires_at
            })
    
    db.session.commit()
    session.pop('cart', None)
    
    return render_template('purchase_success.html', activation_keys=activation_keys)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/add_funds', methods=['POST'])
@login_required
def add_funds():
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Неверная сумма пополнения', 'danger')
            return redirect(url_for('profile'))
        
        current_user.balance += amount
        db.session.commit()
        flash(f'Счет успешно пополнен на ${amount:.2f}', 'success')
    except ValueError:
        flash('Неверный формат суммы', 'danger')
    
    return redirect(url_for('profile'))

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
