from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="football_club"
    )

@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Fetch posts and join with member names
    cursor.execute("SELECT news_feed.*, members.username FROM news_feed JOIN members ON news_feed.member_id = members.id ORDER BY created_at DESC")
    posts = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def post_update():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO news_feed (member_id, content) VALUES (%s, %s)", (session['user_id'], content))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('index'))

@app.route('/download-schedule')
def download_schedule():
    return send_from_directory('static', 'schedule.png', as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)