from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ludiflex_admin:joker1337@34.30.158.137/ludiflex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), default='default.jpg')
    category = db.Column(db.String(50), default='After Effects')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def initialize_database():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            products = [
                Product(
                    name="LZT Motion Pack Vol.1", 
                    description="Professional motion graphics pack for After Effects with 50+ presets",
                    price=49.99,
                    image="product-1.png"
                ),
                Product(
                    name="LZT Transitions Pro", 
                    description="100+ smooth transitions for your video projects",
                    price=29.99,
                    image="product-2.png"
                ),
                Product(
                    name="LZT Text Animations", 
                    description="200+ text animation presets for After Effects",
                    price=39.99,
                    image="product-3.png"
                ),
                Product(
                    name="LZT Particles Universe", 
                    description="Create stunning particle effects with 30+ presets",
                    price=59.99,
                    image="product-4.png"
                )
            ]
            db.session.add_all(products)
            db.session.commit()

@app.route('/')
def index():
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

def index():
    if current_user.is_authenticated:
        products = Product.query.all()
        cart_count = sum(session.get('cart', {}).values())
        return render_template('store.html', products=products, cart_count=cart_count)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверка существующего email
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Аккаунт с таким email уже существует!', 'danger')
            return render_template('register.html', form=form)
        
        # Проверка существующего имени пользователя
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Аккаунт с таким именем пользователя уже существует!', 'danger')
            return render_template('register.html', form=form)
        
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
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Проверка для миграции старых паролей
        if user:
            # Если пароль в формате bcrypt
            if user.password.startswith('$2b$'):
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('index'))
            # Если пароль в открытом виде (старая версия)
            elif user.password == form.password.data:
                # Конвертируем в bcrypt
                user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
        
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
    
    # Определяем откуда пришел запрос и возвращаем обратно
    referrer = request.referrer or url_for('products')
    return redirect(referrer)

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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
