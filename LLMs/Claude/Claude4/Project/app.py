import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-please-change')

    # Build DATABASE_URL from individual vars if not set
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        host = os.environ.get('MYSQL_HOST', '127.0.0.1')
        port = os.environ.get('MYSQL_PORT', '3306')
        user = os.environ.get('MYSQL_USER', 'root')
        password = os.environ.get('MYSQL_PASSWORD', '123')
        db_name = os.environ.get('MYSQL_DB', 'football_club_db')
        db_url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}'

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB upload limit

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Custom Jinja filters
    from markupsafe import Markup, escape

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        return Markup('<br>'.join(str(escape(line)) for line in text.splitlines()))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.news import news_bp
    from routes.schedule import schedule_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(schedule_bp)

    # Create tables
    with app.app_context():
        db.create_all()
        _seed_schedule(app)

    return app


def _seed_schedule(app):
    """Insert default schedule entries if table is empty."""
    from models import ScheduleMatch
    if ScheduleMatch.query.count() == 0:
        matches = [
            ScheduleMatch(date='2025-08-10', time='15:00', opponent='FC Riverside',   location='Home', competition='League'),
            ScheduleMatch(date='2025-08-17', time='14:00', opponent='United Hawks',   location='Away', competition='League'),
            ScheduleMatch(date='2025-08-24', time='15:00', opponent='Red Lions FC',   location='Home', competition='Cup'),
            ScheduleMatch(date='2025-08-31', time='13:00', opponent='City Wolves',    location='Away', competition='League'),
            ScheduleMatch(date='2025-09-07', time='15:00', opponent='Valley FC',      location='Home', competition='League'),
            ScheduleMatch(date='2025-09-14', time='14:00', opponent='Eastern Stars',  location='Away', competition='Cup'),
            ScheduleMatch(date='2025-09-21', time='15:00', opponent='North United',   location='Home', competition='League'),
            ScheduleMatch(date='2025-09-28', time='13:00', opponent='Coastal Rovers', location='Away', competition='League'),
            ScheduleMatch(date='2025-10-05', time='15:00', opponent='Greenfield FC',  location='Home', competition='League'),
            ScheduleMatch(date='2025-10-12', time='14:00', opponent='Thunder City',   location='Away', competition='Cup'),
        ]
        db.session.add_all(matches)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
