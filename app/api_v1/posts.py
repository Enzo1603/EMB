from flask import jsonify, request, g, url_for, current_app
from app import db
from app.models.roles_model import Permission
from app.models.posts_model import Post

from . import api_v1_bp
from .decorators import permission_required
from .errors import forbidden


@api_v1_bp.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page,
        per_page=current_app.config['EMB_POSTS_PER_PAGE'],
        error_out=False,
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1_bp.get_posts', page=page-1)
    next_page = None

    if pagination.has_next:
        next_page = url_for('api_v1_bp.get_posts', page=page+1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next_page,
        'count': pagination.total,
    })


@api_v1_bp.route('/posts/<int:id>/')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api_v1_bp.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api_v1_bp.get_post', id=post.id)}


@api_v1_bp.route('/posts/<int:id>/', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
