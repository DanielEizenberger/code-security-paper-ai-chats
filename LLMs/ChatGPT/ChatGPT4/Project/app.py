from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_file
)

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models.models import db, User, Post

import os


app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('dashboard.html', posts=posts)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        new_post = Post(
            title=title,
            content=content,
            author=current_user
        )

        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_post.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


@app.route('/download-schedule')
def download_schedule():
    schedule_path = os.path.join(
        app.root_path,
        'static/images/schedule.png'
    )

    return send_file(
        schedule_path,
        as_attachment=True,
        download_name='football_schedule.png'
    )


@app.cli.command('create-admin')
def create_admin():
    username = 'admin'
    password = generate_password_hash('admin123')

    if User.query.filter_by(username=username).first():
        print('Admin already exists.')
        return

    admin = User(
        username=username,
        password=password,
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()

    print('Admin created successfully!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)
