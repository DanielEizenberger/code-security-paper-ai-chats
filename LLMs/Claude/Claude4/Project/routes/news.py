from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import NewsPost

news_bp = Blueprint('news', __name__, url_prefix='/news')

CATEGORIES = ['General', 'Match Report', 'Transfer', 'Training', 'Club News', 'Youth']


@news_bp.route('/')
def index():
    category = request.args.get('category', '')
    page     = request.args.get('page', 1, type=int)
    query    = NewsPost.query.order_by(NewsPost.pinned.desc(), NewsPost.created_at.desc())
    if category and category in CATEGORIES:
        query = query.filter_by(category=category)
    pagination = query.paginate(page=page, per_page=8, error_out=False)
    return render_template('news/index.html',
                           posts=pagination.items,
                           pagination=pagination,
                           categories=CATEGORIES,
                           active_category=category)


@news_bp.route('/<int:post_id>')
def detail(post_id):
    post = NewsPost.query.get_or_404(post_id)
    return render_template('news/detail.html', post=post)


@news_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    error = None
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        body     = request.form.get('body', '').strip()
        category = request.form.get('category', 'General')
        pinned   = bool(request.form.get('pinned'))

        if not title or not body:
            error = 'Title and body are required.'
        elif category not in CATEGORIES:
            error = 'Invalid category.'
        else:
            post = NewsPost(title=title, body=body, category=category,
                            pinned=pinned, author_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post published!', 'success')
            return redirect(url_for('news.detail', post_id=post.id))

    return render_template('news/form.html', post=None, categories=CATEGORIES, error=error)


@news_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = NewsPost.query.get_or_404(post_id)
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)

    error = None
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        body     = request.form.get('body', '').strip()
        category = request.form.get('category', 'General')
        pinned   = bool(request.form.get('pinned'))

        if not title or not body:
            error = 'Title and body are required.'
        elif category not in CATEGORIES:
            error = 'Invalid category.'
        else:
            post.title    = title
            post.body     = body
            post.category = category
            post.pinned   = pinned
            db.session.commit()
            flash('Post updated!', 'success')
            return redirect(url_for('news.detail', post_id=post.id))

    return render_template('news/form.html', post=post, categories=CATEGORIES, error=error)


@news_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = NewsPost.query.get_or_404(post_id)
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('news.index'))
