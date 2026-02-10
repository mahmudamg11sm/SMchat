from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models.user import User
from models.post import Post
from app import db

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
@login_required
def home():
    users = User.query.filter(User.id != current_user.id).all()
    unread = Post.query.filter_by(read=False).all()
    return render_template("pages/home.html", users=users, unread=unread)


@pages_bp.route("/chat/<username>", methods=["GET", "POST"])
@login_required
def chat(username):
    other = User.query.filter_by(username=username).first_or_404()

    if request.method == "POST":
        text = request.form.get("text")
        if text:
            msg = Post(
                author_id=current_user.id,
                content=text,
                is_public=False
            )
            db.session.add(msg)
            db.session.commit()

    messages = Post.query.order_by(Post.created_at.asc()).all()
    return render_template(
        "pages/chat.html",
        other=other,
        messages=messages
    )


@pages_bp.route("/search")
@login_required
def search():
    q = request.args.get("q")
    result = None
    if q:
        result = User.query.filter_by(username=q).first()
    return render_template("pages/search.html", result=result)
