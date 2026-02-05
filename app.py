import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from database import init_db, get_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smchat-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

USERS = {}   # sid -> username
ONLINE = set()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def connect():
    pass

@socketio.on("join")
def join(data):
    username = data["username"]
    USERS[request.sid] = username
    ONLINE.add(username)

    emit("online_users", list(ONLINE), broadcast=True)

@socketio.on("disconnect")
def disconnect():
    user = USERS.pop(request.sid, None)
    if user:
        ONLINE.discard(user)
        emit("online_users", list(ONLINE), broadcast=True)

# ======================
# Typing indicator
# ======================
@socketio.on("typing")
def typing(data):
    emit("typing", {
        "from": USERS.get(request.sid),
        "to": data.get("to"),
        "room": data.get("room")
    }, broadcast=True)

# ======================
# Messages
# ======================
@socketio.on("private_message")
def private_message(data):
    sender = USERS.get(request.sid)
    to = data["to"]
    msg = data["msg"]

    db = get_db()
    db.execute(
        "INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
        (sender, to, msg)
    )
    db.commit()

    emit("private_message", {
        "from": sender,
        "msg": msg,
        "status": "delivered"
    }, broadcast=True)

@socketio.on("seen")
def seen(data):
    emit("seen", {
        "from": data.get("from"),
        "to": data.get("to")
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
