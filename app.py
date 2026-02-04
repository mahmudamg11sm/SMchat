import os
from flask import Flask, render_template, request

app = Flask(__name__)

messages = []

@app.route("/", methods=["GET", "POST"])
def chat():
    username = "Mahmudsm1"

    if request.method == "POST":
        text = request.form.get("message")
        messages.append({
            "sender": username,
            "text": text
        })

    return render_template("chat.html", username=username, messages=messages)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
