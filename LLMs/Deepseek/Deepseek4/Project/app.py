from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from config import Config
from schedule_download import generate_schedule_image

app = Flask(__name__)
app.config.from_object(Config)

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

# Login required decorator for members
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'member_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    # Show news feed to everyone
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT news_posts.*, members.username 
        FROM news_posts 
        JOIN members ON news_posts.member_id = members.id 
        ORDER BY news_posts.created_at DESC
    ''')
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM members WHERE username = %s', (username,))
        member = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if member and check_password_hash(member['password_hash'], password):
            session['member_id'] = member['id']
            session['username'] = member['username']
            session['is_admin'] = member['is_admin']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT news_posts.*, members.username 
        FROM news_posts 
        JOIN members ON news_posts.member_id = members.id 
        WHERE members.id = %s
        ORDER BY news_posts.created_at DESC
    ''', (session['member_id'],))
    my_posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('dashboard.html', posts=my_posts)

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO news_posts (member_id, title, content) VALUES (%s, %s, %s)',
            (session['member_id'], title, content)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Post published successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_post.html')

@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    # Only allow deletion if user is admin or post owner
    cursor.execute(
        'DELETE FROM news_posts WHERE id = %s AND (member_id = %s OR %s = TRUE)',
        (post_id, session['member_id'], session.get('is_admin', False))
    )
    connection.commit()
    cursor.close()
    connection.close()
    flash('Post deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/download_schedule')
def download_schedule():
    """Public route to download schedule as PNG"""
    # Generate fresh schedule image
    img_path = generate_schedule_image()
    if img_path and os.path.exists(img_path):
        return send_file(img_path, mimetype='image/png', as_attachment=True, download_name='game_schedule.png')
    else:
        flash('Schedule image not available.', 'danger')
        return redirect(url_for('index'))

@app.route('/schedule')
def schedule():
    """Show schedule preview page"""
    return render_template('schedule.html')

if __name__ == '__main__':
    # Generate schedule image on startup
    generate_schedule_image()
    app.run(debug=True, host='0.0.0.0', port=5000)