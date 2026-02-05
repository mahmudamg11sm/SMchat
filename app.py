import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, emit
import sqlite3

# ================== FLASK SETUP ==================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "smchat-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ================== DATABASE ==================
DB_FILE = "chat.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    # messages table
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        room TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, args)
    r = c.fetchall()
    conn.commit()
    conn.close()
    return (r[0] if r else None) if one else r

init_db()

# ================== GLOBALS ==================
USERS = {}  # sid -> username
ROOMS = {"General"}  # default group
ONLINE = set()

# ================== ROUTES ==================
@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = query_db("SELECT * FROM users WHERE username=? AND password=?", (username, password), one=True)
        if user:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        if password != confirm:
            return render_template("register.html", error="Passwords do not match")
        try:
            query_db("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
            session["username"] = username
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# ================== SOCKET.IO ==================
@socketio.on("connect")
def connect():
    pass

@socketio.on("join")
def on_join(data):
    username = data["username"]
    USERS[request.sid] = username
    ONLINE.add(username)
    emit("online_users", list(ONLINE), broadcast=True)
    emit("users_list", list(USERS.values()), broadcast=True)
    emit("rooms_list", list(ROOMS), broadcast=True)

@socketio.on("disconnect")
def disconnect():
    user = USERS.pop(request.sid, None)
    if user:
        ONLINE.discard(user)
        emit("online_users", list(ONLINE), broadcast=True)
        emit("users_list", list(USERS.values()), broadcast=True)

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
        "msg": f"{USERS.get(request.sid)} has joined the room"
    }, room=room)

@socketio.on("room_message")
def room_message(data):
    room = data["room"]
    msg = data["msg"]
    sender = USERS.get(request.sid)
    query_db("INSERT INTO messages (sender, room, message) VALUES (?,?,?)", (sender, room, msg))
    emit("room_message", {"room": room, "from": sender, "msg": msg}, room=room)

@socketio.on("private_message")
def private_message(data):
    to = data["to"]
    msg = data["msg"]
    sender = USERS.get(request.sid)
    query_db("INSERT INTO messages (sender, receiver, message) VALUES (?,?,?)", (sender, to, msg))
    for sid, user in USERS.items():
        if user == to:
            emit("private_message", {"from": sender, "msg": msg}, room=sid)

@socketio.on("seen")
def seen(data):
    emit("seen", {"from": data.get("from"), "to": data.get("to")}, broadcast=True)

@socketio.on("typing")
def typing(data):
    emit("typing", {
        "from": USERS.get(request.sid),
        "to": data.get("to"),
        "room": data.get("room")
    }, broadcast=True)

# ================== RUN SERVER ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
