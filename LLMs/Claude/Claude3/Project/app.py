from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fc-ironwall-secret-2024-change-in-prod')

# ── MySQL config (override via environment variables in production) ──────────
app.config['MYSQL_HOST']     = '127.0.0.1'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB']       = 'football_club'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ── Context processor (inject `now` into all templates) ──────────────────────
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# ── Auth decorator ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'member_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, m.full_name AS author_name
        FROM posts p
        JOIN members m ON p.member_id = m.id
        ORDER BY p.created_at DESC
        LIMIT 10
    """)
    posts = cur.fetchall()
    cur.close()
    return render_template('index.html', posts=posts)


@app.route('/news')
def news():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, m.full_name AS author_name
        FROM posts p
        JOIN members m ON p.member_id = m.id
        ORDER BY p.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    return render_template('news.html', posts=posts)


@app.route('/news/post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title   = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General')

        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('create_post'))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO posts (member_id, title, content, category) VALUES (%s, %s, %s, %s)",
            (session['member_id'], title, content, category)
        )
        mysql.connection.commit()
        cur.close()
        flash('Post published successfully!', 'success')
        return redirect(url_for('news'))

    return render_template('create_post.html')


@app.route('/news/<int:post_id>')
def view_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.*, m.full_name AS author_name
        FROM posts p
        JOIN members m ON p.member_id = m.id
        WHERE p.id = %s
    """, (post_id,))
    post = cur.fetchone()
    cur.close()
    if not post:
        flash('Post not found.', 'danger')
        return redirect(url_for('news'))
    return render_template('view_post.html', post=post)


@app.route('/news/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT member_id FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if post and post['member_id'] == session['member_id']:
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        mysql.connection.commit()
        flash('Post deleted.', 'success')
    else:
        flash('Not authorised to delete this post.', 'danger')
    cur.close()
    return redirect(url_for('news'))


@app.route('/schedule')
def schedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM matches ORDER BY match_date ASC")
    matches = cur.fetchall()
    cur.close()
    return render_template('schedule.html', matches=matches)


@app.route('/schedule/download')
def download_schedule():
    """Generate and serve a schedule PNG image."""
    from schedule_image import generate_schedule_png

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM matches ORDER BY match_date ASC")
    matches = cur.fetchall()
    cur.close()

    img_bytes = generate_schedule_png(matches)
    return send_file(
        io.BytesIO(img_bytes),
        mimetype='image/png',
        as_attachment=True,
        download_name='fc_ironwall_schedule.png'
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'member_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members WHERE email = %s AND is_active = 1", (email,))
        member = cur.fetchone()
        cur.close()

        if member and check_password_hash(member['password_hash'], password):
            session['member_id']   = member['id']
            session['member_name'] = member['full_name']
            flash(f"Welcome back, {member['full_name']}!", 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Self-registration — requires an invite code set as env var."""
    invite_code = os.environ.get('INVITE_CODE', 'IRONWALL2024')

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        code      = request.form.get('invite_code', '').strip()
        position  = request.form.get('position', 'Player')

        if code != invite_code:
            flash('Invalid invite code.', 'danger')
            return redirect(url_for('register'))

        if not all([full_name, email, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO members (full_name, email, password_hash, position) VALUES (%s, %s, %s, %s)",
                (full_name, email, hashed, position)
            )
            mysql.connection.commit()
            cur.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Email already registered.', 'danger')

    return render_template('register.html')


@app.route('/members')
@login_required
def members():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, full_name, position, joined_at FROM members WHERE is_active=1 ORDER BY full_name")
    members_list = cur.fetchall()
    cur.close()
    return render_template('members.html', members=members_list)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
