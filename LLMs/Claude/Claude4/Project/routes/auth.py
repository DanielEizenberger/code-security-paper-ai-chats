from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import Member

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    error = None
    if request.method == 'POST':
        username     = request.form.get('username', '').strip()
        email        = request.form.get('email', '').strip().lower()
        display_name = request.form.get('display_name', '').strip()
        password     = request.form.get('password', '')
        confirm      = request.form.get('confirm_password', '')

        # Validation
        if not all([username, email, display_name, password, confirm]):
            error = 'All fields are required.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif Member.query.filter_by(username=username).first():
            error = 'Username already taken.'
        elif Member.query.filter_by(email=email).first():
            error = 'Email already registered.'
        else:
            member = Member(username=username, email=email, display_name=display_name)
            member.set_password(password)
            # First registered user becomes admin
            if Member.query.count() == 0:
                member.role = 'admin'
            db.session.add(member)
            db.session.commit()
            flash('Account created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', error=error)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        member = Member.query.filter_by(username=username).first()
        if member and member.check_password(password) and member.is_active:
            login_user(member, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            error = 'Invalid username or password.'

    return render_template('auth/login.html', error=error)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/members')
@login_required
def members():
    """Members list — only accessible when logged in."""
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    all_members = Member.query.order_by(Member.joined_at.desc()).all()
    return render_template('auth/members.html', members=all_members)


@auth_bp.route('/members/<int:member_id>/toggle', methods=['POST'])
@login_required
def toggle_member(member_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    member = Member.query.get_or_404(member_id)
    if member.id == current_user.id:
        flash('You cannot deactivate yourself.', 'warning')
    else:
        member.is_active = not member.is_active
        db.session.commit()
        status = 'activated' if member.is_active else 'deactivated'
        flash(f'Member {member.username} has been {status}.', 'success')
    return redirect(url_for('auth.members'))


@auth_bp.route('/members/<int:member_id>/promote', methods=['POST'])
@login_required
def promote_member(member_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.index'))
    member = Member.query.get_or_404(member_id)
    member.role = 'admin' if member.role == 'member' else 'member'
    db.session.commit()
    flash(f'{member.username} role updated to {member.role}.', 'success')
    return redirect(url_for('auth.members'))
