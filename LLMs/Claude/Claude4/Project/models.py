from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager, bcrypt


@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))


class Member(db.Model, UserMixin):
    """Club member / user account."""
    __tablename__ = 'members'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name  = db.Column(db.String(100), nullable=False)
    role          = db.Column(db.String(20),  nullable=False, default='member')  # 'member' | 'admin'
    joined_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    posts = db.relationship('NewsPost', back_populates='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<Member {self.username}>'


class NewsPost(db.Model):
    """News / update post visible on the public feed."""
    __tablename__ = 'news_posts'

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    body       = db.Column(db.Text,        nullable=False)
    category   = db.Column(db.String(50),  nullable=False, default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id  = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    pinned     = db.Column(db.Boolean, default=False)

    author = db.relationship('Member', back_populates='posts')

    def __repr__(self):
        return f'<NewsPost {self.id}: {self.title[:40]}>'


class ScheduleMatch(db.Model):
    """Single match in the season schedule."""
    __tablename__ = 'schedule_matches'

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.String(10),  nullable=False)   # YYYY-MM-DD
    time        = db.Column(db.String(5),   nullable=False)   # HH:MM
    opponent    = db.Column(db.String(100), nullable=False)
    location    = db.Column(db.String(10),  nullable=False)   # 'Home' | 'Away'
    competition = db.Column(db.String(50),  nullable=False, default='League')
    result      = db.Column(db.String(20),  nullable=True)    # e.g. '2-1'

    def __repr__(self):
        return f'<Match {self.date} vs {self.opponent}>'
