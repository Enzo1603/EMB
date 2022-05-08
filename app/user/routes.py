import os

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.user.forms import ChangeProfileImageForm, EditProfileAdminForm, EditProfileForm
from app.main.image_handler import change_profile_image
from app.models.posts_model import Post
from app.models.roles_model import Permission, Role

from app.models.users_model import User
from app.user import user_bp
from app import db
from app.decorators import permission_required


@user_bp.route("/<string:username>/", methods=["GET", "POST"])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    form = ChangeProfileImageForm()
    if form.validate_on_submit():
        if not form.reset_profile_image.data:
            if form.new_profile_image.data:
                username = user.username
                image = change_profile_image(form.new_profile_image.data, username)
                user.profile_image = image
                db.session.commit()
                flash("Your Profile Image has been changed.")
        elif user.profile_image != "default_profile_image.jpg":
            image_file_name = user.profile_image
            image_file_path = os.path.join(
                current_app.root_path, r"static/main/images/profile-images", image_file_name)
            os.remove(image_file_path)
            user.profile_image = "default_profile_image.jpg"
            db.session.commit()
            flash("Your Profile Image has been reset.")
        return redirect(url_for("user_bp.profile", username=user.username))

    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config["EMB_POSTS_PER_PAGE"],
        error_out=False,
    )
    posts = pagination.items
    return render_template("user/profile.html", user=user, form=form, posts=posts, pagination=pagination)


@user_bp.route("/<string:username>/edit-profile/", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    if current_user.is_administrator():
        form = EditProfileAdminForm(user=user)
    else:
        form = EditProfileForm(user=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.username = form.username.data

        if current_user.is_administrator():
            user.email = form.email.data
            user.confirmed = form.confirmed.data
            if form.new_password.data:
                user.password = form.new_password.data

            user.role = Role.query.get(form.role.data)

        user.location = form.location.data
        user.about_me = form.about_me.data

        db.session.commit()
        flash("Account Information has been updated.")

        return redirect(url_for("user_bp.profile", username=user.username))

    form.name.data = user.name
    form.username.data = user.username

    if current_user.is_administrator():
        form.email.data = user.email
        form.confirmed.data = user.confirmed
        form.role.data = user.role_id

    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit_profile.html', form=form, user=user)


@user_bp.route("/follow/<string:username>/")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    if current_user.username == username:
        flash("You cannot follow yourself.")
        return redirect(url_for("user_bp.profile", username=current_user.username))

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash("You are already following this user.")
        return redirect(url_for("user_bp.profile", username=user.username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}.")
    return redirect(url_for("user_bp.profile", username=username))


@user_bp.route('/unfollow/<string:username>/')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash("You are not following this user.")
        return redirect(url_for('user_bp.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You are not following {username} anymore.")
    return redirect(url_for('user_bp.profile', username=username))


@user_bp.route("/followers/<string:username>/")
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config["EMB_FOLLOWERS_PER_PAGE"],
        error_out=False,
    )
    followers = [{"user": item.follower, "timestamp": item.timestamp} for item in pagination.items]
    return render_template("user/followers.html", user=user, title="Followers of",
                           endpoint="user_bp.followers", pagination=pagination, followers=followers)


@user_bp.route('/followed_by/<string:username>/')
def followed_by(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page,
        per_page=current_app.config['EMB_FOLLOWERS_PER_PAGE'],
        error_out=False
    )

    followeds = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('user/followeds.html', user=user, title="Followed by", endpoint='.followed_by',
                           pagination=pagination, followeds=followeds)
