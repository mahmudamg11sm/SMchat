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
    app.run(debug=True)
