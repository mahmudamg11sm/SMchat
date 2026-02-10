import os
from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "smchat-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(f"{UPLOAD_FOLDER}/images", exist_ok=True)
os.makedirs(f"{UPLOAD_FOLDER}/videos", exist_ok=True)
os.makedirs(f"{UPLOAD_FOLDER}/avatars", exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database
db_path = "instance/database.db"
os.makedirs("instance", exist_ok=True)
db = sqlite3.connect(db_path, check_same_thread=False)
c = db.cursor()

# Tables
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS profiles(
    username TEXT PRIMARY KEY,
    avatar TEXT,
    bio TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    text TEXT,
    type TEXT,
    media_url TEXT
)
""")
db.commit()

USERS = {}  # sid -> username

# ---------------- ROUTES ----------------

@app.route("/", methods=["GET"])
def index():
    if "user" in session:
        return redirect("/home")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        p = c.fetchone()
        if p and p[0]==password:
            session["user"]=username
            return redirect("/home")
        return render_template("auth/login.html", error="Invalid credentials")
    return render_template("auth/login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        c.execute("INSERT OR IGNORE INTO users(username,password) VALUES(?,?)",(username,password))
        db.commit()
        session["user"]=username
        return redirect("/home")
    return render_template("auth/register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("pages/home.html", current_user=session["user"], theme="dark")

@app.route("/profile/<username>")
def profile(username):
    c.execute("SELECT avatar,bio FROM profiles WHERE username=?", (username,))
    p = c.fetchone()
    avatar = p[0] if p else None
    bio = p[1] if p else ""
    return render_template("pages/profile.html", username=username, avatar=avatar, bio=bio)

@app.route("/edit-profile", methods=["GET","POST"])
def edit_profile():
    if "user" not in session:
        return redirect("/login")
    if request.method=="POST":
        bio = request.form.get("bio","")
        avatar=None
        file=request.files.get("avatar")
        if file and file.filename:
            name = secure_filename(file.filename)
            path=f"{UPLOAD_FOLDER}/avatars/{name}"
            file.save(path)
            avatar=path
        c.execute("""
        INSERT INTO profiles(username,avatar,bio)
        VALUES(?,?,?)
        ON CONFLICT(username)
        DO UPDATE SET avatar=excluded.avatar,bio=excluded.bio
        """,(session["user"],avatar,bio))
        db.commit()
        return redirect(f"/profile/{session['user']}")
    return render_template("pages/edit_profile.html")

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ---------------- SOCKET ----------------

@socketio.on("join")
def join(data):
    username=session.get("user")
    if not username:
        return
    USERS[request.sid]=username
    join_room(username)
    emit("users_list", list(USERS.values()), broadcast=True)

@socketio.on("private_message")
def private_message(data):
    sender=USERS.get(request.sid)
    to=data["to"]
    text=data.get("msg","")
    media=data.get("media",None)
    media_url=None
    mtype="text"
    if media:
        file=media
        name=secure_filename(file["name"])
        ext=name.split(".")[-1].lower()
        folder="images" if ext in {"png","jpg","jpeg","gif"} else "videos"
        path=f"{UPLOAD_FOLDER}/{folder}/{name}"
        with open(path,"wb") as f:
            f.write(bytes(file["data"]))
        media_url=path
        mtype="image" if folder=="images" else "video"
    c.execute("INSERT INTO messages(sender,receiver,text,type,media_url) VALUES(?,?,?,?,?)",
             (sender,to,text,mtype,media_url))
    db.commit()
    emit("private_message",{"from":sender,"msg":text,"type":mtype,"media_url":media_url}, room=to)
    emit("private_message",{"from":sender,"msg":text,"type":mtype,"media_url":media_url}, room=sender)

@socketio.on("typing")
def typing(data):
    to = data.get("to")
    if to and to in USERS.values():
        emit("typing", {"from":USERS.get(request.sid)}, room=to)

@socketio.on("seen")
def seen(data):
    to=data.get("to")
    emit("seen", {"to":USERS.get(request.sid)}, room=to)

@socketio.on("disconnect")
def disconnect():
    USERS.pop(request.sid,None)
    emit("users_list", list(USERS.values()), broadcast=True)

# ---------------- RUN ----------------
if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    socketio.run(app, host="0.0.0.0", port=port)
