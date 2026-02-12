import os
from flask import Flask, render_template, request, redirect, session, send_from_directory, g
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from models.user import User
from models.post import Post
from models.message import Message
import sqlite3

# ------------------ APP SETUP ------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smchat-secret")

UPLOAD_FOLDER = "static/uploads"
IMAGE_EXT = {"png", "jpg", "jpeg", "gif"}
VIDEO_EXT = {"mp4", "webm", "mov"}

IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")

for folder in [UPLOAD_FOLDER, IMAGE_FOLDER, VIDEO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ------------------ DATABASE ------------------
DATABASE = "instance/database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)""")
    # Profiles table
    c.execute("""CREATE TABLE IF NOT EXISTS profiles(username TEXT PRIMARY KEY, avatar TEXT, bio TEXT)""")
    # Messages table
    c.execute("""CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    receiver TEXT,
                    text TEXT,
                    type TEXT,
                    media_url TEXT,
                    status TEXT DEFAULT 'sent'
                )""")
    # Posts table
    c.execute("""CREATE TABLE IF NOT EXISTS posts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    content TEXT
                )""")
    db.commit()
    db.close()

if not os.path.exists("instance"):
    os.makedirs("instance")

init_db()

# ------------------ ONLINE USERS ------------------
ONLINE_USERS = set()

# ------------------ ROUTES ------------------

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    posts = Post.all()
    return render_template("pages/home.html", posts=posts)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.get(username)
        if user and user.password == password:
            session["user"] = username
            return redirect("/")
        return render_template("auth/login.html", error="Invalid credentials")
    return render_template("auth/login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            User.create(username, password)
            session["user"] = username
            return redirect("/")
        except sqlite3.IntegrityError:
            return render_template("auth/register.html", error="Username exists")
    return render_template("auth/register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT avatar,bio FROM profiles WHERE username=?", (username,))
    p = c.fetchone()
    avatar = p["avatar"] if p else None
    bio = p["bio"] if p else ""
    return render_template("pages/profile.html", username=username, avatar=avatar, bio=bio)

@app.route("/edit-profile", methods=["GET","POST"])
def edit_profile():
    if "user" not in session:
        return redirect("/login")
    if request.method=="POST":
        bio = request.form.get("bio","")
        avatar = None
        file = request.files.get("avatar")
        if file and file.filename:
            name = secure_filename(file.filename)
            ext = name.rsplit(".",1)[-1].lower()
            if ext in IMAGE_EXT:
                path = os.path.join(IMAGE_FOLDER,name)
            elif ext in VIDEO_EXT:
                path = os.path.join(VIDEO_FOLDER,name)
            else:
                path = os.path.join(UPLOAD_FOLDER,name)
            file.save(path)
            avatar = path
        db = get_db()
        c = db.cursor()
        c.execute("""
            INSERT INTO profiles(username,avatar,bio)
            VALUES(?,?,?)
            ON CONFLICT(username) DO UPDATE SET avatar=excluded.avatar,bio=excluded.bio
        """,(session["user"],avatar,bio))
        db.commit()
        return redirect(f"/profile/{session['user']}")
    db = get_db()
    c = db.cursor()
    c.execute("SELECT bio FROM profiles WHERE username=?",(session["user"],))
    bio_row = c.fetchone()
    bio = bio_row["bio"] if bio_row else ""
    return render_template("pages/edit_profile.html", bio=bio)

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/chat/<username>")
def chat(username):
    if "user" not in session:
        return redirect("/login")
    messages = Message.get_conversation(session["user"], username)
    return render_template("pages/chat.html", friend=username, messages=messages)

@app.route("/search")
def search():
    q = request.args.get("q","")
    result = None
    if q:
        user = User.get(q)
        if user:
            result = {"username": user.username}
    return render_template("pages/search.html", result=result)

# ------------------ SOCKET.IO EVENTS ------------------

@socketio.on("connect")
def on_connect():
    user = session.get("user")
    if user:
        ONLINE_USERS.add(user)
        emit("user_status", {"user": user, "status":"online"}, broadcast=True)

@socketio.on("disconnect")
def on_disconnect():
    user = session.get("user")
    if user in ONLINE_USERS:
        ONLINE_USERS.remove(user)
        emit("user_status", {"user": user, "status":"offline"}, broadcast=True)

@socketio.on("join_room")
def handle_join(data):
    room = data.get("room")
    if room:
        join_room(room)

@socketio.on("private_message")
def private_message(data):
    sender = session.get("user")
    receiver = data.get("to")
    text = data.get("msg")
    if not sender or not receiver or not text:
        return
    status = "delivered" if receiver in ONLINE_USERS else "sent"
    Message.create(sender, receiver, text, status=status)
    room = "_".join(sorted([sender, receiver]))
    emit("private_message", {"from": sender, "msg": text, "status":status}, room=room)

@socketio.on("seen")
def mark_seen(data):
    sender = data.get("sender")
    receiver = session.get("user")
    if not sender or not receiver:
        return
    Message.mark_seen(sender, receiver)
    room = "_".join(sorted([sender, receiver]))
    emit("message_seen", {"sender": sender}, room=room)

@socketio.on("delete_message")
def delete_message(data):
    text = data.get("text")
    sender = session.get("user")
    if text and sender:
        Message.delete(sender, text)

# ------------------ REACTIONS SYSTEM ------------------

REACTIONS = {}  # (sender, receiver, msg_id) -> {emoji: count}

@socketio.on("reaction")
def send_reaction(data):
    sender = session.get("user")
    receiver = data.get("to")
    emoji = data.get("emoji")
    text = data.get("text")
    key = (sender, receiver, text)
    if key not in REACTIONS:
        REACTIONS[key] = {}
    REACTIONS[key][emoji] = REACTIONS[key].get(emoji,0)+1
    emit("reaction", {"from": sender, "to": receiver, "emoji": emoji, "text": text, "count": REACTIONS[key][emoji]},
         room="_".join(sorted([sender, receiver])))

# ------------------ MAIN ------------------
if __name__=="__main__":
    port = int(os.environ.get("PORT",10000))
    socketio.run(app, host="0.0.0.0", port=port)
