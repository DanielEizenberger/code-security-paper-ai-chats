import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database import Database
from schedule_generator import generate_schedule_png
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'football_secret_key_2024')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = Database()

class User(UserMixin):
    def __init__(self, id, username, email, is_member):
        self.id = id
        self.username = username
        self.email = email
        self.is_member = is_member

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'], user_data['is_member'])
    return None

@app.route('/')
def index():
    posts = db.get_all_posts()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        if db.create_user(username, email, password_hash):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = db.get_user_by_username(username)
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['email'], user_data['is_member'])
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_member:
        flash('Only club members can access this page.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if db.create_post(current_user.id, title, content):
            flash('News post published!', 'success')
        else:
            flash('Failed to post.', 'danger')
        return redirect(url_for('dashboard'))
    
    my_posts = db.get_posts_by_user(current_user.id)
    return render_template('dashboard.html', my_posts=my_posts)

@app.route('/schedule')
def schedule():
    games = db.get_all_games()
    # Generate fresh PNG every time for up-to-date schedule
    generate_schedule_png(games)
    return render_template('schedule.html', games=games)

@app.route('/download_schedule')
def download_schedule():
    games = db.get_all_games()
    generate_schedule_png(games)
    return send_from_directory('static', 'schedule.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)