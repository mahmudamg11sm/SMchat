import os
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE HELPER ----------
def get_db():
    return sqlite3.connect("chat.db")

# ---------- INIT DATABASE ----------
conn = get_db()
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

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        sender = request.form.get("sender")
        receiver = request.form.get("receiver")
        message = request.form.get("message")
        if sender and receiver and message:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO messages VALUES (?,?,?)", (sender, receiver, message))
            conn.commit()
            conn.close()
        return redirect(f"/?user={sender}")

    user = request.args.get("user", "")
    messages = []
    if user:
        conn = get_db()
        c = conn.cursor()
        # Show only messages where user is sender or receiver
        c.execute("SELECT sender, receiver, message FROM messages WHERE sender=? OR receiver=?", (user, user))
        messages = c.fetchall()
        conn.close()

    return render_template("index.html", messages=messages, user=user)

# ---------- MAIN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
