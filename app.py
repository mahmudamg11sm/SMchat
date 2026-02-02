import os
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE HELPER ----------
def get_db():
    """Return a connection to the SQLite database"""
    return sqlite3.connect("chat.db")

# ---------- INIT DATABASE ----------
conn = get_db()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    sender TEXT,
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
        message = request.form.get("message")
        if sender and message:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO messages VALUES (?,?)", (sender, message))
            conn.commit()
            conn.close()
        return redirect("/")

    # Load messages
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages")
    messages = c.fetchall()
    conn.close()
    
    return render_template("index.html", messages=messages)

# ---------- MAIN ----------
if __name__ == "__main__":
    # Render will set the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
