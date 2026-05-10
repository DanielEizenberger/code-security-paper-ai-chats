from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from config import Config
from models.models import db, Member, Post

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))


@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = Member.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        member = Member(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(member)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        member = Member.query.filter_by(email=email).first()

        if member and bcrypt.check_password_hash(member.password, password):
            login_user(member)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
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

        post = Post(
            title=title,
            content=content,
            member_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_post.html')


@app.route('/download-schedule')
def download_schedule():
    return send_file(
        'static/images/game_schedule.png',
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True)
