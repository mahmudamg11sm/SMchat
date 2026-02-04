import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # sid -> username

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def on_join(data):
    username = data["username"]
    users[request.sid] = username
    emit("users_list", list(users.values()), broadcast=True)

@socketio.on("disconnect")
def on_disconnect():
    users.pop(request.sid, None)
    emit("users_list", list(users.values()), broadcast=True)

@socketio.on("dm")
def handle_dm(data):
    sender = data["sender"]
    receiver = data["receiver"]
    message = data["message"]

    # tura saƙo ga receiver kaɗai
    for sid, uname in users.items():
        if uname == receiver:
            emit("dm_message", {
                "sender": sender,
                "message": message
            }, room=sid)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
