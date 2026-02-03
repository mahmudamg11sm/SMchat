from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
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
    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================
@app.route("/")
def index():
    username = request.args.get("user", "Mahmudsm1")
    return render_template("chat.html", username=username)

# ================= SOCKET EVENTS =================
@socketio.on("send_message")
def handle_message(data):
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

# ================= MAIN =================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
