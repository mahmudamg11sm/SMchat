import os
from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import sqlite3

# ------------------ APP SETUP ------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
UPLOAD_FOLDER = "static/uploads"
IMAGE_EXT = {"png","jpg","jpeg","gif"}
VIDEO_EXT = {"mp4","webm","mov"}

IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")

# Ensure folders exist
for folder in [UPLOAD_FOLDER, IMAGE_FOLDER, VIDEO_FOLDER]:
    os.makedirs(folder, exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------ DATABASE ------------------
if not os.path.exists("instance"):
    os.makedirs("instance")

db_path = "instance/database.db"
db = sqlite3.connect(db_path, check_same_thread=False)
c = db.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
# Profiles table
c.execute("""
CREATE TABLE IF NOT EXISTS profiles(
    username TEXT PRIMARY KEY,
    avatar TEXT,
    bio TEXT
)
""")
# Messages table
c.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    text TEXT,
    type TEXT,
    media_url TEXT
)
""")
# Posts table
c.execute("""
CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    content TEXT
)
""")
db.commit()

# ------------------ SESSION USERS ------------------
USERS = {}  # sid -> username

# ------------------ ROUTES ------------------

# Home
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("pages/home.html")

# Login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if row and row[0] == password:
            session["user"] = username
            return redirect("/")
        return render_template("auth/login.html", error="Invalid credentials")
    return render_template("auth/login.html")

# Register
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            c.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))
            db.commit()
            session["user"] = username
            return redirect("/")
        except:
            return render_template("auth/register.html", error="Username exists")
    return render_template("auth/register.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# Profile
@app.route("/profile/<username>")
def profile(username):
    c.execute("SELECT avatar,bio FROM profiles WHERE username=?", (username,))
    p = c.fetchone()
    avatar = p[0] if p else None
    bio = p[1] if p else ""
    return render_template("pages/profile.html", username=username, avatar=avatar, bio=bio)

# Edit profile
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
            ext = name.rsplit(".", 1)[-1].lower()
            if ext in IMAGE_EXT:
                path = os.path.join(IMAGE_FOLDER, name)
            elif ext in VIDEO_EXT:
                path = os.path.join(VIDEO_FOLDER, name)
            else:
                path = os.path.join(UPLOAD_FOLDER, name)
            file.save(path)
            avatar = path
        c.execute("""
        INSERT INTO profiles(username,avatar,bio)
        VALUES(?,?,?)
        ON CONFLICT(username) DO UPDATE SET avatar=excluded.avatar,bio=excluded.bio
        """,(session["user"],avatar,bio))
        db.commit()
        return redirect(f"/profile/{session['user']}")
    c.execute("SELECT bio FROM profiles WHERE username=?",(session["user"],))
    bio_row = c.fetchone()
    bio = bio_row[0] if bio_row else ""
    return render_template("pages/edit_profile.html", bio=bio)

# Uploads serving
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Public posts
@app.route("/public")
def public():
    c.execute("SELECT user,content FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    return render_template("pages/public.html", posts=posts)

# Search user
@app.route("/search")
def search():
    q = request.args.get("q","")
    result = None
    if q:
        c.execute("SELECT username FROM users WHERE username=?",(q,))
        row = c.fetchone()
        if row:
            result = {"username": row[0]}
    return render_template("pages/search.html", result=result)

# Private chat page
@app.route("/chat/<username>")
def chat(username):
    if "user" not in session:
        return redirect("/login")

    current_user = session["user"]

    # Get old messages between users
    c.execute("""
        SELECT sender, text FROM messages
        WHERE (sender=? AND receiver=?)
        OR (sender=? AND receiver=?)
        ORDER BY id ASC
    """, (current_user, username, username, current_user))

    messages = c.fetchall()

    return render_template("pages/chat.html",
                           friend=username,
                           messages=messages)
    
# ------------------ SOCKET.IO ------------------
@socketio.on("connect")
def on_connect():
    print("Client connected")

@socketio.on("disconnect")
def on_disconnect():
    sid_user = USERS.pop(request.sid, None)
    print(f"{sid_user} disconnected")

@socketio.on("join_room")
def handle_join(data):
    room = data.get("room")
    join_room(room)

@socketio.on("private_message")
def private_message(data):
    sender = session.get("user")
    receiver = data.get("to")
    text = data.get("msg")

    if not sender or not receiver:
        return

    # Save message
    c.execute("""
        INSERT INTO messages(sender,receiver,text,type)
        VALUES(?,?,?,?)
    """,(sender,receiver,text,"text"))
    db.commit()

    # Create room name
    room = "_".join(sorted([sender, receiver]))

    emit("private_message",
         {"from": sender, "msg": text},
         room=room)
    
# ------------------ MAIN ------------------
if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    socketio.run(app, host="0.0.0.0", port=port)
