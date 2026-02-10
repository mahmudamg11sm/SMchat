from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from app import db
from models.message import Message
from models.user import User

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("/chat/<username>", methods=["GET", "POST"])
@login_required
def chat(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404

    if request.method == "POST":
        text = request.form.get("message")
        if text:
            msg = Message(
                sender=current_user.username,
                receiver=username,
                content=text
            )
            db.session.add(msg)
            db.session.commit()
            return redirect(f"/chat/{username}")

    messages = Message.query.filter(
        ((Message.sender == current_user.username) & (Message.receiver == username)) |
        ((Message.sender == username) & (Message.receiver == current_user.username))
    ).order_by(Message.timestamp).all()

    return render_template(
        "pages/chat.html",
        messages=messages,
        user=username
            )
