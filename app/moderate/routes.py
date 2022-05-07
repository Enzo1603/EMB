from flask import current_app, redirect, render_template, request, url_for
from flask_login import login_required
from app import db
from app.models.comments_model import Comment
from app.models.roles_model import Permission
from app.moderate import moderate_bp
from app.decorators import permission_required


@moderate_bp.route("/")
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config["EMB_COMMENTS_PER_PAGE"],
        error_out=False,
    )
    comments = pagination.items
    return render_template("moderate/moderate.html", comments=comments, pagination=pagination, page=page)


@moderate_bp.route('/moderate/enable/<int:comment_id>/')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


@moderate_bp.route('/moderate/disable/<int:comment_id>/')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))
