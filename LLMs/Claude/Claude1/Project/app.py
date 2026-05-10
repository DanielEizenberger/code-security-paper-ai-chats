"""
app.py – FC Ironclad website (Flask + MySQL/SQLite)
"""

import os
import functools
import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, send_file, abort,
)
import io
import db
import schedule_image

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-please")

# ── Bootstrap database ───────────────────────────────────────────────────────
db.init_db()


# ════════════════════════════════════════════════════════════════════════════
# Auth helpers
# ════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "member_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "member_id" not in session:
            flash("Please log in.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

def current_member():
    if "member_id" in session:
        return {"id": session["member_id"], "username": session["username"], "role": session["role"]}
    return None


# ════════════════════════════════════════════════════════════════════════════
# Context processor
# ════════════════════════════════════════════════════════════════════════════

@app.context_processor
def inject_user():
    return {"member": current_member()}


# ════════════════════════════════════════════════════════════════════════════
# Public routes
# ════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    posts = db.list_posts(limit=20)
    return render_template("index.html", posts=posts)


@app.route("/schedule")
def schedule():
    fixtures = db.list_fixtures()
    return render_template("schedule.html", fixtures=fixtures)


@app.route("/schedule/download")
def download_schedule():
    """Return the fixture list rendered as a PNG image."""
    png_bytes = schedule_image.generate_schedule_png()
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name="fc_ironclad_schedule.png",
    )


# ════════════════════════════════════════════════════════════════════════════
# Auth routes
# ════════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if "member_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        member   = db.authenticate_member(username, password)

        if member:
            session["member_id"] = member["id"]
            session["username"]  = member["username"]
            session["role"]      = member["role"]
            flash(f"Welcome back, {member['username']}!", "success")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════════════════════
# Members-only: news posts
# ════════════════════════════════════════════════════════════════════════════

@app.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body  = request.form.get("body", "").strip()

        if not title or not body:
            flash("Title and body are required.", "danger")
        else:
            db.create_post(session["member_id"], title, body)
            flash("Post published!", "success")
            return redirect(url_for("index"))

    return render_template("new_post.html")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int):
    # Only admins can delete any post; members can only delete their own
    # (for simplicity we allow admins only via admin panel below)
    if session.get("role") != "admin":
        abort(403)
    db.delete_post(post_id)
    flash("Post deleted.", "info")
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════════════════════
# Admin panel
# ════════════════════════════════════════════════════════════════════════════

@app.route("/admin")
@admin_required
def admin_panel():
    members  = db.list_members()
    posts    = db.list_posts(limit=100)
    fixtures = db.list_fixtures()
    return render_template("admin.html", members=members, posts=posts, fixtures=fixtures)


@app.route("/admin/members/create", methods=["POST"])
@admin_required
def admin_create_member():
    username = request.form.get("username", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    role     = request.form.get("role", "member")

    if not username or not email or not password:
        flash("All fields are required.", "danger")
    elif db.create_member(username, email, password, role):
        flash(f"Member '{username}' created.", "success")
    else:
        flash("Username or email already exists.", "danger")

    return redirect(url_for("admin_panel"))


@app.route("/admin/members/<int:member_id>/delete", methods=["POST"])
@admin_required
def admin_delete_member(member_id: int):
    if member_id == session["member_id"]:
        flash("You cannot delete your own account.", "danger")
    else:
        db.delete_member(member_id)
        flash("Member deleted.", "info")
    return redirect(url_for("admin_panel"))


@app.route("/admin/fixtures/add", methods=["POST"])
@admin_required
def admin_add_fixture():
    try:
        db.add_fixture(
            request.form["match_date"],
            request.form["kick_off"],
            request.form["home_team"],
            request.form["away_team"],
            request.form["venue"],
            request.form["competition"],
        )
        flash("Fixture added.", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("admin_panel"))


@app.route("/admin/fixtures/<int:fixture_id>/result", methods=["POST"])
@admin_required
def admin_set_result(fixture_id: int):
    result = request.form.get("result", "").strip()
    db.update_fixture_result(fixture_id, result or None)
    flash("Result updated.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/fixtures/<int:fixture_id>/delete", methods=["POST"])
@admin_required
def admin_delete_fixture(fixture_id: int):
    db.delete_fixture(fixture_id)
    flash("Fixture removed.", "info")
    return redirect(url_for("admin_panel"))


@app.route("/admin/posts/<int:post_id>/delete", methods=["POST"])
@admin_required
def admin_delete_post(post_id: int):
    db.delete_post(post_id)
    flash("Post deleted.", "info")
    return redirect(url_for("admin_panel"))


# ════════════════════════════════════════════════════════════════════════════
# Run
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
