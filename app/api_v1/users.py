from flask import jsonify, request, current_app, url_for
from . import api_v1_bp
from app.models.posts_model import Post
from app.models.users_model import User


@api_v1_bp.route('/users/<int:id>/')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api_v1_bp.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['EMB_POSTS_PER_PAGE'],
        error_out=False,
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1_bp.get_user_posts', id=id, page=page-1)
    next_page = None

    if pagination.has_next:
        next_page = url_for('api_v1_bp.get_user_posts', id=id, page=page+1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next_page,
        'count': pagination.total
    })


@api_v1_bp.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['EMB_POSTS_PER_PAGE'],
        error_out=False,
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1_bp.get_user_followed_posts', id=id, page=page-1)
    next_page = None

    if pagination.has_next:
        next_page = url_for('api_v1_bp.get_user_followed_posts', id=id, page=page+1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next_page,
        'count': pagination.total
    })
