import os
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import database as db

app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "static/uploads"
IMAGE_EXT = {"png","jpg","jpeg","gif"}
VIDEO_EXT = {"mp4","webm","mov"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

USERS = {}  # sid -> username
ROOMS = {"General"}

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ---------------- SOCKET EVENTS ----------------
@socketio.on("join")
def join(data):
    username = data["username"]
    USERS[request.sid] = username
    room = data.get("room", "General")
    join_room(room)
    emit("system", f"{username} joined {room}", room=room)
    emit("users_list", list(USERS.values()), broadcast=True)
    emit("rooms_list", list(ROOMS), broadcast=True)
    # add member to db
    db.c.execute("INSERT OR IGNORE INTO users(username) VALUES(?)", (username,))
    db.db.commit()

@socketio.on("create_channel")
def create_channel(data):
    name = data["name"]
    admin = USERS.get(request.sid)
    db.c.execute("INSERT OR IGNORE INTO channels(name,admin) VALUES(?,?)", (name,admin))
    db.c.execute("INSERT OR IGNORE INTO members(user,channel) VALUES(?,?)", (admin,name))
    db.db.commit()
    emit("channels_list", [c[0] for c in db.c.execute("SELECT name FROM channels")], broadcast=True)

@socketio.on("join_channel")
def join_channel(data):
    channel = data["channel"]
    user = USERS.get(request.sid)
    db.c.execute("INSERT OR IGNORE INTO members(user,channel) VALUES(?,?)", (user,channel))
    db.db.commit()
    join_room(channel)
    emit("system", f"{user} joined {channel}", room=channel)

@socketio.on("channel_message")
def channel_message(data):
    user = USERS.get(request.sid)
    channel = data["channel"]
    text = data.get("text","")
    media = data.get("media",None)

    media_url = None
    mtype = "text"
    if media:
        file = media
        name = secure_filename(file["name"])
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
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path,"wb") as f:
            f.write(bytes(file["data"]))
        media_url = path

    db.c.execute("INSERT INTO messages(sender,channel,text,type,media_url) VALUES(?,?,?,?,?)",
                 (user,channel,text,mtype,media_url))
    db.db.commit()

    emit("new_channel_message", {"sender":user,"channel":channel,"text":text,"type":mtype,"media_url":media_url}, room=channel)

@socketio.on("comment")
def comment(data):
    db.c.execute("INSERT INTO comments(message_id,commenter,text) VALUES(?,?,?)",
                 (data["msg_id"],USERS.get(request.sid),data["text"]))
    db.db.commit()
    emit("new_comment", data, room=data["channel"])

@socketio.on("like")
def like(data):
    db.c.execute("INSERT INTO likes(message_id,user) VALUES(?,?)",
                 (data["msg_id"],USERS.get(request.sid)))
    db.db.commit()
    emit("new_like", data, room=data["channel"])

@socketio.on("disconnect")
def disconnect():
    username = USERS.pop(request.sid,None)
    emit("users_list", list(USERS.values()), broadcast=True)
    if username:
        emit("system", f"{username} disconnected", broadcast=True)

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    socketio.run(app,host="0.0.0.0",port=port)
