"""
FC Irongate - Football Club Website
Flask + SQLite (MySQL-compatible SQL syntax)
"""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file, g, abort
)
from schedule_gen import generate_schedule_image

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = os.path.join(os.path.dirname(__file__), "instance", "club.db")
SCHEDULE_PATH = os.path.join(os.path.dirname(__file__), "static", "img", "schedule.png")

# ── Database helpers ────────────────────────────────────────────────────────────
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    """Create tables (MySQL-compatible DDL)."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with sqlite3.connect(DATABASE) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS members (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  VARCHAR(80)  NOT NULL UNIQUE,
                email     VARCHAR(120) NOT NULL UNIQUE,
                password  VARCHAR(256) NOT NULL,
                role      VARCHAR(20)  NOT NULL DEFAULT 'member',
                joined_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS news_posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      VARCHAR(200) NOT NULL,
                body       TEXT         NOT NULL,
                author_id  INTEGER      NOT NULL REFERENCES members(id),
                created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                category   VARCHAR(40)  NOT NULL DEFAULT 'General'
            );
        """)
        # Seed an admin account if none exists
        cur = db.execute("SELECT COUNT(*) FROM members WHERE role='admin'")
        if cur.fetchone()[0] == 0:
            pw = hash_password("Admin1234!")
            db.execute(
                "INSERT INTO members (username, email, password, role) VALUES (?,?,?,?)",
                ("admin", "admin@fcirongate.com", pw, "admin")
            )
            # Seed a few news posts
            seed_posts = [
                ("Season Kick-off Press Conference",
                 "We are thrilled to announce the start of a new season! The squad has been training hard all summer and the manager is confident about our title challenge this year. Tickets go on sale next Monday.",
                 1, "Club News"),
                ("New Signing: Marcus Steele",
                 "FC Irongate is proud to welcome midfielder Marcus Steele from Riverside FC. Marcus brings 8 years of top-flight experience and will wear the number 8 shirt. Welcome to the Irongate family!",
                 1, "Transfers"),
                ("Youth Academy Open Day – June 14",
                 "Our award-winning Youth Academy is hosting an Open Day for players aged 8–16. Come and meet the coaches, tour the facilities, and find out how to join the academy programme.",
                 1, "Academy"),
            ]
            db.executemany(
                "INSERT INTO news_posts (title, body, author_id, category) VALUES (?,?,?,?)",
                seed_posts
            )
        db.commit()

# ── Auth helpers ────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f"{salt}${h}"

def check_password(stored: str, provided: str) -> bool:
    try:
        salt, h = stored.split("$", 1)
        return hashlib.sha256((salt + provided).encode()).hexdigest() == h
    except Exception:
        return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated

def current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    return db.execute("SELECT * FROM members WHERE id=?", (session["user_id"],)).fetchone()

# ── Routes ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    db = get_db()
    posts = db.execute("""
        SELECT p.*, m.username AS author_name
        FROM   news_posts p
        JOIN   members m ON m.id = p.author_id
        ORDER  BY p.created_at DESC
        LIMIT  20
    """).fetchall()
    return render_template("index.html", posts=posts, user=current_user())


@app.route("/news/<int:post_id>")
def news_detail(post_id):
    db = get_db()
    post = db.execute("""
        SELECT p.*, m.username AS author_name
        FROM   news_posts p
        JOIN   members m ON m.id = p.author_id
        WHERE  p.id = ?
    """, (post_id,)).fetchone()
    if not post:
        abort(404)
    return render_template("news_detail.html", post=post, user=current_user())


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        body     = request.form.get("body", "").strip()
        category = request.form.get("category", "General").strip()
        errors = []
        if not title:
            errors.append("Title is required.")
        if not body:
            errors.append("Post body is required.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("new_post.html", user=current_user(),
                                   title=title, body=body, category=category)
        db = get_db()
        db.execute(
            "INSERT INTO news_posts (title, body, author_id, category) VALUES (?,?,?,?)",
            (title, body, session["user_id"], category)
        )
        db.commit()
        flash("Post published successfully!", "success")
        return redirect(url_for("index"))
    return render_template("new_post.html", user=current_user())


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    db = get_db()
    post = db.execute("SELECT * FROM news_posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        abort(404)
    u = current_user()
    if post["author_id"] != u["id"] and u["role"] != "admin":
        abort(403)
    db.execute("DELETE FROM news_posts WHERE id=?", (post_id,))
    db.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        pw       = request.form.get("password", "")
        pw2      = request.form.get("password2", "")
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if len(pw) < 6:
            errors.append("Password must be at least 6 characters.")
        if pw != pw2:
            errors.append("Passwords do not match.")
        db = get_db()
        if db.execute("SELECT id FROM members WHERE username=?", (username,)).fetchone():
            errors.append("That username is already taken.")
        if db.execute("SELECT id FROM members WHERE email=?", (email,)).fetchone():
            errors.append("That email is already registered.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html", user=None,
                                   username=username, email=email)
        db.execute(
            "INSERT INTO members (username, email, password) VALUES (?,?,?)",
            (username, email, hash_password(pw))
        )
        db.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", user=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    next_url = request.args.get("next", url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        pw       = request.form.get("password", "")
        db = get_db()
        member = db.execute("SELECT * FROM members WHERE username=?", (username,)).fetchone()
        if not member or not check_password(member["password"], pw):
            flash("Invalid username or password.", "danger")
            return render_template("login.html", user=None, username=username)
        session["user_id"] = member["id"]
        session["username"] = member["username"]
        flash(f"Welcome back, {member['username']}!", "success")
        return redirect(next_url)
    return render_template("login.html", user=None)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/schedule")
def schedule():
    return render_template("schedule.html", user=current_user())


@app.route("/schedule/download")
def download_schedule():
    """Public endpoint – anyone can download the schedule PNG."""
    if not os.path.exists(SCHEDULE_PATH):
        generate_schedule_image(SCHEDULE_PATH)
    return send_file(SCHEDULE_PATH, mimetype="image/png",
                     as_attachment=True, download_name="fc_irongate_schedule.png")


@app.route("/members")
@login_required
def members_list():
    db = get_db()
    members = db.execute(
        "SELECT id, username, email, role, joined_at FROM members ORDER BY joined_at"
    ).fetchall()
    return render_template("members.html", members=members, user=current_user())


# ── Template context ─────────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    return {"now": datetime.utcnow()}

# ── Error pages ─────────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="Page not found.", user=current_user()), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403,
                           message="You don't have permission to do that.", user=current_user()), 403


# ── Entry point ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    generate_schedule_image(SCHEDULE_PATH)
    app.run(debug=True, port=5000)
