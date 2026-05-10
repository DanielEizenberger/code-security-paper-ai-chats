from flask import Blueprint, render_template
from models import NewsPost, ScheduleMatch

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    pinned  = NewsPost.query.filter_by(pinned=True).order_by(NewsPost.created_at.desc()).first()
    recent  = NewsPost.query.filter_by(pinned=False).order_by(NewsPost.created_at.desc()).limit(3).all()
    upcoming = ScheduleMatch.query.order_by(ScheduleMatch.date).limit(3).all()
    return render_template('main/index.html', pinned=pinned, recent=recent, upcoming=upcoming)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')
