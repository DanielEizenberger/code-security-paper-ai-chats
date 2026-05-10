from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from flask_bcrypt import Bcrypt
from config import Config
from datetime import datetime
import os

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    member_id = db.Column(
        db.Integer,
        db.ForeignKey('members.id'),
        nullable=False
    )


# =====================================================
# LOGIN MANAGER
# =====================================================

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))

# =====================================================
# ROUTES
# =====================================================
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = Member.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_member = Member(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_member)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        member = Member.query.filter_by(email=email).first()

        if member and bcrypt.check_password_hash(member.password, password):
            login_user(member)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid credentials.', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    my_posts = Post.query.filter_by(member_id=current_user.id).all()
    return render_template('dashboard.html', posts=my_posts)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        new_post = Post(
            title=title,
            content=content,
            member_id=current_user.id
        )

        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create_post.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# =====================================================
# PUBLIC SCHEDULE DOWNLOAD
# =====================================================

@app.route('/download-schedule')
def download_schedule():

    file_path = os.path.join(
        app.root_path,
        'static',
        'schedules',
        'season_schedule.png'
    )

    return send_file(
        file_path,
        mimetype='image/png',
        as_attachment=True,
        download_name='football_club_schedule.png'
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    app.run(debug=True)