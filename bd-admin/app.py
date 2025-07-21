from flask import Flask, redirect, url_for, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from markupsafe import Markup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ludiflex_admin:joker1337@34.30.158.137:5432/ludiflex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ======= МОДЕЛИ =======

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

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    balance = db.Column(db.Float)

# ======= FAKE ADMIN USER =======

class AdminUser(UserMixin):
    id = 1
    username = "admin"
    password = "joker1337"

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return AdminUser()
    return None

# ======= КЛАССЫ ADMIN VIEWS С ЗАЩИТОЙ =======

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class UserView(AuthenticatedModelView):
    column_list = ('id', 'username', 'email', 'password', 'balance')

class PackageView(AuthenticatedModelView):
    column_list = ('id', 'name', 'description', 'price', 'folder_path')

class ProductView(AuthenticatedModelView):
    column_list = ('id', 'name', 'description', 'price', 'image', 'category')

class PurchaseView(AuthenticatedModelView):
    column_list = ('id', 'user_id', 'package_id', 'key_id', 'purchase_date')

class ActivationKeyView(AuthenticatedModelView):
    column_list = ('id', 'package_id', 'key', 'user_id', 'created_at', 'expires_at', 'used')

# ======= КАСТОМНЫЙ INDEX VIEW =======

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        username = current_user.username
        logout_url = url_for('logout')
        html = f"""
        <div class="container">
            <h2>Привет, {username}!</h2>
            <a href="{logout_url}" class="btn btn-danger">Выйти</a>
        </div>
        """
        return self.render('admin/custom_index.html', content=Markup(html))

# ======= ИНИЦИАЛИЗАЦИЯ ADMIN =======

admin = Admin(app, name='Админка Ludiflex', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(UserView(User, db.session))
admin.add_view(PackageView(Package, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(PurchaseView(Purchase, db.session))
admin.add_view(ActivationKeyView(ActivationKey, db.session))

# ======= ROUTES LOGIN/LOGOUT =======

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "joker1337":
            user = AdminUser()
            login_user(user)
            flash("Успешный вход", "success")
            return redirect(url_for('admin.index'))
        else:
            flash("Неверный логин или пароль", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ======= ЗАПУСК =======

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
