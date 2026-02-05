import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

# ========================
# App Configuration
# ========================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smchat-secret")

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

# ========================
# In-memory storage
# (Za mu mayar da DB daga baya)
# ========================
USERS = {}          # sid -> username
ROOMS = {"General"} # default room

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
    emit("rooms_list", list(ROOMS))

@socketio.on("join")
def on_join(data):
    username = data.get("username", "").strip()

    if not username:
        emit("error", {"msg": "Username ya zama dole"})
        return

    if username in USERS.values():
        emit("error", {"msg": "Username yana amfani"})
        return

    USERS[request.sid] = username

    emit("users_list", list(USERS.values()), broadcast=True)
    emit("system_message", {
        "msg": f"{username} ya shiga chat"
    }, broadcast=True)

@socketio.on("private_message")
def private_message(data):
    to_user = data.get("to")
    msg = data.get("msg", "").strip()
    sender = USERS.get(request.sid)

    if not msg or not to_user:
        return

    for sid, username in USERS.items():
        if username == to_user:
            emit("private_message", {
                "from": sender,
                "msg": msg
            }, room=sid)
            break

@socketio.on("create_room")
def create_room_event(data):
    room = data.get("room", "").strip()

    if not room:
        emit("error", {"msg": "Room name ba zai zama babu komai ba"})
        return

    if room in ROOMS:
        emit("error", {"msg": "Room tuni yana akwai"})
        return

    ROOMS.add(room)
    emit("rooms_list", list(ROOMS), broadcast=True)

@socketio.on("join_room")
def join_room_event(data):
    room = data.get("room")

    if room not in ROOMS:
        emit("error", {"msg": "Room baya wanzuwa"})
        return

    join_room(room)

    emit("room_message", {
        "room": room,
        "from": "System",
        "msg": f"{USERS.get(request.sid)} ya shiga group"
    }, room=room)

@socketio.on("leave_room")
def leave_room_event(data):
    room = data.get("room")

    leave_room(room)

    emit("room_message", {
        "room": room,
        "from": "System",
        "msg": f"{USERS.get(request.sid)} ya fita daga group"
    }, room=room)

@socketio.on("room_message")
def room_message(data):
    room = data.get("room")
    msg = data.get("msg", "").strip()

    if not msg:
        return

    emit("room_message", {
        "room": room,
        "from": USERS.get(request.sid),
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
# Run App
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
