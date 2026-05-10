from flask import Flask, render_template, request, redirect, session, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123',
    'database': 'football_club'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ---------- Public Routes ----------
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT news_posts.*, members.username 
        FROM news_posts 
        JOIN members ON news_posts.member_id = members.id 
        ORDER BY news_posts.created_at DESC
    ''')
    posts = cursor.fetchall()
    
    cursor.execute('SELECT * FROM game_schedule ORDER BY match_date')
    schedule = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('index.html', posts=posts, schedule=schedule)

@app.route('/schedule.png')
def schedule_png():
    """Generate schedule as PNG for public download"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM game_schedule ORDER BY match_date')
    schedule = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Create image
    img_width = 800
    img_height = 100 + 60 * (len(schedule) + 1)
    image = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Header
    draw.text((img_width//2 - 150, 20), "⚽ FC CHAMPIONS SCHEDULE ⚽", fill="darkgreen", font=font_title)
    
    # Table headers
    y = 80
    draw.text((30, y), "Date", fill="black", font=font_text)
    draw.text((200, y), "Opponent", fill="black", font=font_text)
    draw.text((450, y), "Location", fill="black", font=font_text)
    draw.text((650, y), "H/A", fill="black", font=font_text)
    y += 30
    draw.line([(20, y), (img_width-20, y)], fill="gray", width=2)
    
    # Rows
    for match in schedule:
        y += 35
        draw.text((30, y), str(match['match_date']), fill="black", font=font_text)
        draw.text((200, y), match['opponent'], fill="black", font=font_text)
        draw.text((450, y), match['location'] or '-', fill="black", font=font_text)
        draw.text((650, y), match['home_away'], fill="blue" if match['home_away'] == 'Home' else "red", font=font_text)
    
    # Footer
    y += 50
    draw.text((30, y), "⚡ Download from official club website", fill="gray", font=font_text)
    
    # Save to bytes and return
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='fc_champions_schedule.png')

# ---------- Authentication Routes ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO members (username, email, password_hash) VALUES (%s, %s, %s)',
                           (username, email, password))
            conn.commit()
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            return "Username or email already exists"
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM members WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['member_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------- Member-Only Routes ----------
@app.route('/dashboard')
def dashboard():
    if 'member_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT news_posts.*, members.username 
        FROM news_posts 
        JOIN members ON news_posts.member_id = members.id 
        ORDER BY news_posts.created_at DESC
    ''')
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', posts=posts, username=session['username'])

@app.route('/post', methods=['POST'])
def create_post():
    if 'member_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO news_posts (member_id, title, content) VALUES (%s, %s, %s)',
                   (session['member_id'], title, content))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'member_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only allow deletion if admin or post owner (simplified: only admin or owner)
    cursor.execute('SELECT member_id FROM news_posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    if post and (post[0] == session['member_id'] or session.get('is_admin')):
        cursor.execute('DELETE FROM news_posts WHERE id = %s', (post_id,))
        conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)