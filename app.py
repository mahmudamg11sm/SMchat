import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
import sqlite3

# ================== APP ==================
app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# ================== UPLOAD ==================
UPLOAD_FOLDER = "static/uploads"
IMAGE_EXT = {"png", "jpg", "jpeg", "gif"}
VIDEO_EXT = {"mp4", "webm", "mov"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(f"{UPLOAD_FOLDER}/images", exist_ok=True)
os.makedirs(f"{UPLOAD_FOLDER}/videos", exist_ok=True)

# ================== DATABASE ==================
def get_db():
    return sqlite3.connect("chat.db", check_same_thread=False)

db = get_db()
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender TEXT,
  channel TEXT,
  text TEXT,
  type TEXT,
  media_url TEXT
)
""")

db.commit()

# ================== MEMORY ==================
USERS = {}   # sid -> username
ROOMS = {"General"}

# ================== ROUTES ==================
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", username=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if c.fetchone():
            session["user"] = u
            return redirect("/")
        return "Invalid login"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        try:
            c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u, p))
            db.commit()
            return redirect("/login")
        except:
            return "Username already exists"

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ================== SOCKET ==================
@socketio.on("join")
def join(data):
    username = data["username"]
    USERS[request.sid] = username
    room = data.get("room", "General")

    join_room(room)

    emit("system", f"{username} joined {room}", room=room)
    emit("users_list", list(USERS.values()), broadcast=True)
    emit("rooms_list", list(ROOMS), broadcast=True)

@socketio.on("channel_message")
def channel_message(data):
    sender = USERS.get(request.sid)
    channel = data["channel"]
    text = data.get("text", "")
    media = data.get("media")

    media_url = None
    mtype = "text"

    if media:
        name = secure_filename(media["name"])
        ext = name.split(".")[-1].lower()

        if ext in IMAGE_EXT:
            folder = "images"
            mtype = "image"
        elif ext in VIDEO_EXT:
            folder = "videos"
            mtype = "video"
        else:
            return

        path = f"{UPLOAD_FOLDER}/{folder}/{name}"
        with open(path, "wb") as f:
            f.write(bytes(media["data"]))

        media_url = path

    c.execute(
        "INSERT INTO messages(sender,channel,text,type,media_url) VALUES(?,?,?,?,?)",
        (sender, channel, text, mtype, media_url)
    )
    db.commit()

    emit("new_channel_message", {
        "sender": sender,
        "channel": channel,
        "text": text,
        "type": mtype,
        "media_url": media_url
    }, room=channel)

@socketio.on("disconnect")
def disconnect():
    USERS.pop(request.sid, None)
    emit("users_list", list(USERS.values()), broadcast=True)

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
