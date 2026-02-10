from flask import Blueprint, render_template
from flask_login import login_required

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/home")
@login_required
def home():
    return render_template("pages/home.html")

@pages_bp.route("/public")
@login_required
def public():
    return render_template("pages/public.html")

@pages_bp.route("/notifications")
@login_required
def notifications():
    return render_template("pages/notifications.html")

@pages_bp.route("/search")
@login_required
def search():
    return render_template("pages/search.html")

@pages_bp.route("/users")
@login_required
def users():
    return render_template("pages/users.html")

@pages_bp.route("/info")
@login_required
def info():
    return render_template("pages/info.html")
