from flask import Blueprint, render_template, request
from flask_login import login_required
from models.user import User

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
@login_required
def home():
    return render_template("pages/home.html")

@pages_bp.route("/search")
@login_required
def search():
    q = request.args.get("q")
    result = None
    if q:
        result = User.query.filter_by(username=q).first()
    return render_template("pages/search.html", result=result)
