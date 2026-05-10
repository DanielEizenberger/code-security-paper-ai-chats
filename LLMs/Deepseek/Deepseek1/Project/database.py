import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'football_club'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'autocommit': True
        }
    
    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def create_user(self, username, email, password_hash):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            cursor.close()
            conn.close()
            return True
        except Error:
            return False
    
    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    
    def create_post(self, user_id, title, content):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO news_posts (user_id, title, content) VALUES (%s, %s, %s)",
                (user_id, title, content)
            )
            cursor.close()
            conn.close()
            return True
        except Error:
            return False
    
    def get_all_posts(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT news_posts.*, users.username 
            FROM news_posts 
            JOIN users ON news_posts.user_id = users.id 
            ORDER BY news_posts.created_at DESC
        """)
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        return posts
    
    def get_posts_by_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM news_posts WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        return posts
    
    def get_all_games(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM games ORDER BY game_date ASC")
        games = cursor.fetchall()
        cursor.close()
        conn.close()
        return games