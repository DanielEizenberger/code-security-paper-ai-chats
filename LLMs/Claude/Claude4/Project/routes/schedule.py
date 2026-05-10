import io
from flask import Blueprint, render_template, send_file, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import ScheduleMatch
from schedule_image import generate_schedule_image

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/')
def index():
    matches = ScheduleMatch.query.order_by(ScheduleMatch.date).all()
    return render_template('schedule/index.html', matches=matches)


@schedule_bp.route('/download')
def download():
    """Generate and serve the schedule as a PNG — publicly accessible."""
    matches = ScheduleMatch.query.order_by(ScheduleMatch.date).all()
    img_bytes = generate_schedule_image(matches)
    return send_file(
        io.BytesIO(img_bytes),
        mimetype='image/png',
        as_attachment=True,
        download_name='FC_Ironclad_Schedule_2025.png'
    )


@schedule_bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('schedule.index'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            date        = request.form.get('date', '').strip()
            time        = request.form.get('time', '').strip()
            opponent    = request.form.get('opponent', '').strip()
            location    = request.form.get('location', 'Home')
            competition = request.form.get('competition', 'League')
            if date and time and opponent:
                match = ScheduleMatch(date=date, time=time, opponent=opponent,
                                      location=location, competition=competition)
                db.session.add(match)
                db.session.commit()
                flash('Match added.', 'success')

        elif action == 'result':
            match_id = request.form.get('match_id', type=int)
            result   = request.form.get('result', '').strip()
            match    = ScheduleMatch.query.get(match_id)
            if match:
                match.result = result or None
                db.session.commit()
                flash('Result updated.', 'success')

        elif action == 'delete':
            match_id = request.form.get('match_id', type=int)
            match    = ScheduleMatch.query.get(match_id)
            if match:
                db.session.delete(match)
                db.session.commit()
                flash('Match removed.', 'info')

        return redirect(url_for('schedule.manage'))

    matches = ScheduleMatch.query.order_by(ScheduleMatch.date).all()
    return render_template('schedule/manage.html', matches=matches)
