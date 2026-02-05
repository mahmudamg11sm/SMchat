import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import database as db

app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

USERS = {}

@app.route("/")
def index():
    return render_template("index.html")

# ================= CONNECT =================
@socketio.on("connect")
def connect():
    pass

# ================= JOIN =================
@socketio.on("join")
def join(data):
    username = data["username"]
    USERS[request.sid] = username

    db.c.execute(
        "INSERT OR IGNORE INTO users(username,online) VALUES(?,1)",
        (username,)
    )
    db.db.commit()

    emit("users_list", list(USERS.values()), broadcast=True)

# ================= DISCONNECT =================
@socketio.on("disconnect")
def disconnect():
    user = USERS.pop(request.sid, None)
    if user:
        db.c.execute("UPDATE users SET online=0 WHERE username=?", (user,))
        db.db.commit()

    emit("users_list", list(USERS.values()), broadcast=True)

# ================= ROOM =================
@socketio.on("create_room")
def create_room(data):
    name = data["room"]
    admin = USERS.get(request.sid)

    db.c.execute(
        "INSERT OR IGNORE INTO rooms(name,admin,type) VALUES(?,?,?)",
        (name, admin, "group")
    )
    db.db.commit()

    emit("rooms_list", get_rooms(), broadcast=True)

def get_rooms():
    db.c.execute("SELECT name FROM rooms")
    return [x[0] for x in db.c.fetchall()]

# ================= JOIN ROOM =================
@socketio.on("join_room")
def join_room_event(data):
    join_room(data["room"])
    emit("room_message", {
        "room": data["room"],
        "from": "System",
        "msg": f"{USERS.get(request.sid)} joined"
    }, room=data["room"])

# ================= ROOM MESSAGE =================
@socketio.on("room_message")
def room_message(data):
    sender = USERS.get(request.sid)

    db.c.execute(
        "INSERT INTO messages(sender,room,text,type) VALUES(?,?,?,?)",
        (sender, data["room"], data["msg"], "room")
    )
    db.db.commit()

    emit("room_message", {
        "room": data["room"],
        "from": sender,
        "msg": data["msg"]
    }, room=data["room"])

# ================= DM =================
@socketio.on("private_message")
def private_message(data):
    sender = USERS.get(request.sid)

    db.c.execute(
        "INSERT INTO messages(sender,receiver,text,type) VALUES(?,?,?,?)",
        (sender, data["to"], data["msg"], "dm")
    )
    db.db.commit()

    for sid, user in USERS.items():
        if user == data["to"]:
            emit("private_message", {
                "from": sender,
                "msg": data["msg"]
            }, room=sid)

# ================= LIKE =================
@socketio.on("like")
def like(data):
    db.c.execute(
        "INSERT INTO likes(msg_id,username) VALUES(?,?)",
        (data["msg_id"], USERS.get(request.sid))
    )
    db.db.commit()

# ================= COMMENT =================
@socketio.on("comment")
def comment(data):
    db.c.execute(
        "INSERT INTO comments(msg_id,username,text) VALUES(?,?,?)",
        (data["msg_id"], USERS.get(request.sid), data["text"])
    )
    db.db.commit()

# ================= SEARCH =================
@socketio.on("search")
def search(data):
    q = data["q"]
    db.c.execute(
        "SELECT username FROM users WHERE username=? OR phone=?",
        (q,q)
    )
    r = db.c.fetchone()
    emit("search_result", r[0] if r else None)

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    socketio.run(app,host="0.0.0.0",port=port)
