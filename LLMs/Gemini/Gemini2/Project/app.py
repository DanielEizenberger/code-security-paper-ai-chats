from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'football_club'

mysql = MySQL(app)

# --- Routes ---

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT news.title, news.content, members.username, news.created_at FROM news JOIN members ON news.author_id = members.id ORDER BY news.created_at DESC")
    all_news = cursor.fetchall()
    return render_template('index.html', news=all_news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # In a real app, use password hashing (werkzeug.security)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username FROM members WHERE username = %s", [username])
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/post_news', methods=['POST'])
def post_news():
    if 'user_id' in session:
        title = request.form['title']
        content = request.form['content']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO news (title, content, author_id) VALUES (%s, %s, %s)",
                       (title, content, session['user_id']))
        mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/download-schedule')
def download_schedule():
    # Place 'schedule.png' inside a folder named 'static'
    return send_from_directory(directory='static', path='schedule.png', as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
