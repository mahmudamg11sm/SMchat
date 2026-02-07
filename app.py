import os
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
import database as db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"

# -------- SOCKET --------
socketio = SocketIO(app, cors_allowed_origins="*")

# -------- UPLOAD CONFIG --------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
IMAGE_EXT = {"png", "jpg", "jpeg", "gif"}
VIDEO_EXT = {"mp4", "webm", "mov"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- STATE --------
USERS = {}     # sid -> username
ROOMS = {"General"}

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ================= SOCKET EVENTS =================
@socketio.on("join")
def join(data):
    username = data["username"]
    room = data.get("room", "General")

    USERS[request.sid] = username
    join_room(room)

    emit("system", f"{username} joined {room}", room=room)
    emit("users_list", list(USERS.values()), broadcast=True)
    emit("rooms_list", list(ROOMS), broadcast=True)

    db.c.execute(
        "INSERT OR IGNORE INTO users(username) VALUES(?)",
        (username,)
    )
    db.db.commit()

@socketio.on("create_channel")
def create_channel(data):
    name = data["name"]
    admin = USERS.get(request.sid)

    db.c.execute(
        "INSERT OR IGNORE INTO channels(name,admin) VALUES(?,?)",
        (name, admin)
    )
    db.c.execute(
        "INSERT OR IGNORE INTO members(user,channel) VALUES(?,?)",
        (admin, name)
    )
    db.db.commit()

    channels = [c[0] for c in db.c.execute("SELECT name FROM channels")]
    emit("channels_list", channels, broadcast=True)

@socketio.on("join_channel")
def join_channel(data):
    channel = data["channel"]
    user = USERS.get(request.sid)

    join_room(channel)

    db.c.execute(
        "INSERT OR IGNORE INTO members(user,channel) VALUES(?,?)",
        (user, channel)
    )
    db.db.commit()

    emit("system", f"{user} joined {channel}", room=channel)

@socketio.on("channel_message")
def channel_message(data):
    user = USERS.get(request.sid)
    channel = data["channel"]
    text = data.get("text", "")
    media = data.get("media")

    media_url = None
    mtype = "text"

    if media:
        name = secure_filename(media["name"])
        ext = name.rsplit(".", 1)[-1].lower()

        if ext in IMAGE_EXT:
            folder = "images"
            mtype = "image"
        elif ext in VIDEO_EXT:
            folder = "videos"
            mtype = "video"
        else:
            return

        save_dir = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(save_dir, exist_ok=True)

        path = os.path.join(save_dir, name)
        with open(path, "wb") as f:
            f.write(bytes(media["data"]))

        media_url = f"uploads/{folder}/{name}"

    db.c.execute(
        """INSERT INTO messages
        (sender, channel, text, type, media_url)
        VALUES (?,?,?,?,?)""",
        (user, channel, text, mtype, media_url)
    )
    db.db.commit()

    emit(
        "new_channel_message",
        {
            "sender": user,
            "channel": channel,
            "text": text,
            "type": mtype,
            "media_url": media_url
        },
        room=channel
    )

@socketio.on("comment")
def comment(data):
    db.c.execute(
        "INSERT INTO comments(message_id,commenter,text) VALUES(?,?,?)",
        (data["msg_id"], USERS.get(request.sid), data["text"])
    )
    db.db.commit()

    emit("new_comment", data, room=data["channel"])

@socketio.on("like")
def like(data):
    db.c.execute(
        "INSERT INTO likes(message_id,user) VALUES(?,?)",
        (data["msg_id"], USERS.get(request.sid))
    )
    db.db.commit()

    emit("new_like", data, room=data["channel"])

@socketio.on("disconnect")
def disconnect():
    user = USERS.pop(request.sid, None)
    emit("users_list", list(USERS.values()), broadcast=True)

    if user:
        emit("system", f"{user} disconnected", broadcast=True)

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
