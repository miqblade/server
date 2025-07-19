import os
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yy93kDt8@Zs4vPx1#AjmRwXq9N8LdUq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Preset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    folder = db.Column(db.String(64), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    presets = Preset.query.all()
    return render_template('dashboard.html', presets=presets)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        folder = request.form['folder']
        file = request.files['preset']
        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
            os.makedirs(save_path, exist_ok=True)
            file.save(os.path.join(save_path, filename))
            preset = Preset(filename=filename, folder=folder)
            db.session.add(preset)
            db.session.commit()
            flash('File uploaded successfully')
            return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/download/<int:preset_id>')
@login_required
def download(preset_id):
    preset = Preset.query.get_or_404(preset_id)
    path = os.path.join(app.config['UPLOAD_FOLDER'], preset.folder)
    return send_from_directory(path, preset.filename, as_attachment=True)

def create_tables_and_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('joker1337')  # Замените пароль на безопасный
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_tables_and_admin()
    app.run(debug=True)
