from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        sender TEXT,
        receiver TEXT,
        message TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS group_messages (
        sender TEXT,
        group_name TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= ROUTE =================
@app.route("/")
def index():
    username = request.args.get("user", "Guest")
    return render_template("chat.html", username=username)

# ================= DM CHAT =================
@socketio.on("send_message")
def handle_dm(data):
    sender = data["sender"]
    receiver = data["receiver"]
    message = data["message"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages VALUES (?,?,?)",
        (sender, receiver, message)
    )
    conn.commit()
    conn.close()

    emit("receive_message", data, broadcast=True)

# ================= GROUP JOIN =================
@socketio.on("join_group")
def join_group_chat(data):
    username = data["username"]
    group = data["group"]

    join_room(group)
    emit(
        "group_notice",
        {"msg": f"{username} ya shiga group {group}"},
        room=group
    )

# ================= GROUP MESSAGE =================
@socketio.on("send_group_message")
def handle_group_message(data):
    sender = data["sender"]
    group = data["group"]
    message = data["message"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO group_messages VALUES (?,?,?)",
        (sender, group, message)
    )
    conn.commit()
    conn.close()

    emit("receive_group_message", data, room=group)

# ================= MAIN =================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
