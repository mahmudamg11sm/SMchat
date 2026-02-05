import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from database import get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smchat-secret")

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# in-memory users (sid -> username)
USERS = {}

# ========================
# Init Database
# ========================
init_db()

# ========================
# Routes
# ========================
@app.route("/")
def index():
    return render_template("index.html")

# ========================
# Socket Events
# ========================

@socketio.on("connect")
def on_connect():
    db = get_db()
    rooms = [r["name"] for r in db.execute("SELECT name FROM rooms")]
    emit("rooms_list", rooms)

@socketio.on("join")
def on_join(data):
    username = data.get("username", "").strip()
    if not username:
        emit("error", {"msg": "Username ya zama dole"})
        return

    db = get_db()
    try:
        db.execute("INSERT INTO users (username) VALUES (?)", (username,))
        db.commit()
    except:
        pass

    USERS[request.sid] = username

    emit("users_list", list(USERS.values()), broadcast=True)
    emit("system_message", {
        "msg": f"{username} ya shiga chat"
    }, broadcast=True)

@socketio.on("private_message")
def private_message(data):
    sender = USERS.get(request.sid)
    to_user = data.get("to")
    msg = data.get("msg", "").strip()

    if not msg or not to_user:
        return

    db = get_db()
    db.execute(
        "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
        (sender, to_user, msg)
    )
    db.commit()

    for sid, user in USERS.items():
        if user == to_user:
            emit("private_message", {
                "from": sender,
                "msg": msg
            }, room=sid)
            break

@socketio.on("create_room")
def create_room_event(data):
    room = data.get("room", "").strip()
    if not room:
        return

    db = get_db()
    try:
        db.execute("INSERT INTO rooms (name) VALUES (?)", (room,))
        db.commit()
    except:
        emit("error", {"msg": "Room yana nan tuni"})
        return

    emit("rooms_list", [r["name"] for r in db.execute("SELECT name FROM rooms")], broadcast=True)

@socketio.on("join_room")
def join_room_event(data):
    room = data.get("room")
    join_room(room)

    emit("room_message", {
        "room": room,
        "from": "System",
        "msg": f"{USERS.get(request.sid)} ya shiga group"
    }, room=room)

@socketio.on("room_message")
def room_message(data):
    room = data.get("room")
    msg = data.get("msg", "").strip()
    sender = USERS.get(request.sid)

    if not msg:
        return

    db = get_db()
    db.execute(
        "INSERT INTO messages (sender, room, message) VALUES (?, ?, ?)",
        (sender, room, msg)
    )
    db.commit()

    emit("room_message", {
        "room": room,
        "from": sender,
        "msg": msg
    }, room=room)

@socketio.on("disconnect")
def on_disconnect():
    username = USERS.pop(request.sid, None)
    if username:
        emit("users_list", list(USERS.values()), broadcast=True)
        emit("system_message", {
            "msg": f"{username} ya fita daga chat"
        }, broadcast=True)

# ========================
# Run
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
