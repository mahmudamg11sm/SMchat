from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("chat.db")

# DB init
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

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        sender = request.form["sender"]
        message = request.form["message"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO messages VALUES (?,?)", (sender, message))
        conn.commit()
        conn.close()
        return redirect("/")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages")
    messages = c.fetchall()
    conn.close()

    return render_template("index.html", messages=messages)

if __name__ == "__main__":
    app.run()
