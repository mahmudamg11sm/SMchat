from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models.post import Post
from models.user import User

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.route("/public", methods=["GET", "POST"])
@login_required
def public_feed():
    if request.method == "POST":
        text = request.form.get("text")
        if text:
            post = Post(author_id=current_user.id, content=text, is_public=True)
            db.session.add(post)
            db.session.commit()
        return redirect(url_for("posts.public_feed"))

    posts = Post.query.filter_by(is_public=True).order_by(Post.created_at.desc()).all()
    return render_template("pages/public.html", posts=posts)


@posts_bp.route("/mark-read/<int:post_id>")
@login_required
def mark_read(post_id):
    post = Post.query.get_or_404(post_id)
    post.read = True
    db.session.commit()
    return "", 204
