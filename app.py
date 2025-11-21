from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__, static_folder="static")

# Lista en memoria para guardar mensajes
messages = []

@app.get("/messages")
def get_messages():
    return jsonify(messages)

@app.post("/messages")
def post_message():
    data = request.get_json(force=True)
    user = data.get("user", "anon")
    text = data.get("text", "").strip()
    city = data.get("city", "").strip()

    if not text:
        return jsonify({"error": "Mensaje vacío"}), 400

    msg = {
        "user": user,
        "text": text,
        "city": city,
        "timestamp": datetime.utcnow().isoformat()
    }
    messages.append(msg)
    return jsonify(msg), 201

@app.get("/")
def root():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)