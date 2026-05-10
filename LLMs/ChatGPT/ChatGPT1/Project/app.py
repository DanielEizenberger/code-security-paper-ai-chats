from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------------------
# User Class
# -----------------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM members WHERE id = %s", [user_id])
    user = cur.fetchone()
    cur.close()

    if user:
        return User(user[0], user[1])

    return None

# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def index():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT posts.id, posts.title, posts.content,
               posts.created_at, members.username
        FROM posts
        JOIN members ON posts.member_id = members.id
        ORDER BY posts.created_at DESC
    """)

    posts = cur.fetchall()
    cur.close()

    return render_template("index.html", posts=posts)

# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()

        try:
            cur.execute(
                "INSERT INTO members(username, password) VALUES(%s, %s)",
                (username, password)
            )

            mysql.connection.commit()

            flash("Registration successful!")
            return redirect(url_for("login"))

        except:
            flash("Username already exists.")

        finally:
            cur.close()

    return render_template("register.html")

# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM members WHERE username = %s",
            [username]
        )

        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            login_user(User(user[0], user[1]))
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# Create Post
# -----------------------------
@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO posts(title, content, member_id)
            VALUES(%s, %s, %s)
        """, (title, content, current_user.id))

        mysql.connection.commit()
        cur.close()

        flash("Post created!")
        return redirect(url_for("index"))

    return render_template("create_post.html")

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# -----------------------------
# Download Schedule PNG
# -----------------------------
@app.route("/download-schedule")
def download_schedule():
    return send_file(
        "static/uploads/schedule.png",
        as_attachment=True
    )

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
