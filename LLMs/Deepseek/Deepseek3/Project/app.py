# app.py - Main Flask Application
import os
import io
import hashlib
from datetime import datetime
from functools import wraps
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-12345'

# MySQL Configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123'  # Change this
app.config['MYSQL_DB'] = 'football_club'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Ensure uploads directory exists
os.makedirs('static', exist_ok=True)

# ==================== DATABASE SETUP ====================
# Run these SQL commands once to set up the database
"""
CREATE DATABASE IF NOT EXISTS football_club;
USE football_club;

CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Insert a default admin (username: admin, password: admin123)
INSERT INTO members (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@club.com', 'sha256$abc123...', TRUE)
ON DUPLICATE KEY UPDATE username=username;
"""

# ==================== AUTH DECORATOR ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'member_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'member_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('news_feed'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================
@app.route('/')
def index():
    """Landing page with public information and schedule download"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password)
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO members (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, hashed_pw))
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Username or email already exists.', 'danger')
        finally:
            cur.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, password_hash, is_admin FROM members WHERE username = %s", (username,))
        member = cur.fetchone()
        cur.close()
        
        if member and check_password_hash(member['password_hash'], password):
            session['member_id'] = member['id']
            session['username'] = member['username']
            session['is_admin'] = member['is_admin']
            flash(f'Welcome back, {member["username"]}!', 'success')
            return redirect(url_for('news_feed'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/news')
def news_feed():
    """Public news feed - anyone can read, only members can post via /post-news"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.*, m.username, m.id as author_id 
        FROM news_posts n 
        JOIN members m ON n.member_id = m.id 
        ORDER BY n.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    return render_template('news_feed.html', posts=posts)

@app.route('/post-news', methods=['GET', 'POST'])
@login_required
def post_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form.get('image_url', '')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO news_posts (member_id, title, content, image_url) VALUES (%s, %s, %s, %s)",
                   (session['member_id'], title, content, image_url))
        mysql.connection.commit()
        cur.close()
        
        flash('News post published successfully!', 'success')
        return redirect(url_for('news_feed'))
    
    return render_template('post_news.html')

@app.route('/delete-post/<int:post_id>')
@admin_required
def delete_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM news_posts WHERE id = %s", (post_id,))
    mysql.connection.commit()
    cur.close()
    flash('Post deleted successfully.', 'success')
    return redirect(url_for('news_feed'))

@app.route('/schedule.png')
def download_schedule():
    """Generate and serve the game schedule as PNG - accessible to everyone"""
    # Create an image with schedule data
    img = Image.new('RGB', (800, 600), color=(34, 139, 34))  # Football green background
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Draw title
    draw.text((300, 30), "FC CHAMPIONS - GAME SCHEDULE 2026", fill="white", font=font_title)
    
    # Schedule data (you can modify or fetch from DB)
    schedule = [
        ("May 15, 2026", "Home vs City Rivals", "7:00 PM", "Main Stadium"),
        ("May 22, 2026", "Away at United FC", "5:30 PM", "United Arena"),
        ("June 5, 2026", "Home vs Star FC", "6:00 PM", "Main Stadium"),
        ("June 12, 2026", "Away at Thunder FC", "4:00 PM", "Thunder Dome"),
        ("June 20, 2026", "Home vs Eagles", "7:30 PM", "Main Stadium"),
        ("July 4, 2026", "Championship Semi-Final", "8:00 PM", "Neutral Venue"),
    ]
    
    # Draw headers
    headers = ["Date", "Match", "Time", "Venue"]
    y = 100
    x_positions = [50, 220, 500, 620]
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y), header, fill="yellow", font=font_header)
    
    # Draw each game
    y += 40
    for game in schedule:
        draw.text((x_positions[0], y), game[0], fill="white", font=font_text)
        draw.text((x_positions[1], y), game[1], fill="white", font=font_text)
        draw.text((x_positions[2], y), game[2], fill="white", font=font_text)
        draw.text((x_positions[3], y), game[3], fill="white", font=font_text)
        y += 35
    
    # Add footer
    draw.text((250, 550), "For updates, visit our website | #FCChampions", fill="lightgray", font=font_text)
    
    # Save to bytes and serve
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return send_file(img_bytes, mimetype='image/png', as_attachment=False, download_name='schedule.png')

# ==================== RUN APP ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)