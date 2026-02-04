import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

USERS = {}          # sid -> username
ROOMS = {"General"} # default group

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def connect():
    pass

@socketio.on("join")
def on_join(data):
    username = data["username"]
    USERS[request.sid] = username

    # aika users list
    emit("users_list", list(USERS.values()), broadcast=True)
    emit("rooms_list", list(ROOMS), broadcast=True)

@socketio.on("private_message")
def private_message(data):
    to = data["to"]
    msg = data["msg"]
    sender = USERS.get(request.sid)

    for sid, user in USERS.items():
        if user == to:
            emit("private_message", {
                "from": sender,
                "msg": msg
            }, room=sid)

@socketio.on("create_room")
def create_room(data):
    room = data["room"]
    ROOMS.add(room)
    emit("rooms_list", list(ROOMS), broadcast=True)

@socketio.on("join_room")
def join_room_event(data):
    room = data["room"]
    join_room(room)
    emit("room_message", {
        "room": room,
        "from": "System",
        "msg": f"{USERS.get(request.sid)} ya shiga group"
    }, room=room)

@socketio.on("room_message")
def room_message(data):
    emit("room_message", {
        "room": data["room"],
        "from": USERS.get(request.sid),
        "msg": data["msg"]
    }, room=data["room"])

@socketio.on("disconnect")
def disconnect():
    USERS.pop(request.sid, None)
    emit("users_list", list(USERS.values()), broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
