from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__, static_folder="static")

OPENWEATHER_KEY = "399edb2f7c72b4688028518a3e182f7d"  # pon tu key aquí

# Lista en memoria para mensajes
messages = []

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
    res = requests.get(url, timeout=5).json()
    return f"🌤️ En {city}: {res['main']['temp']} °C, {res['weather'][0]['description']}"

@app.get("/messages")
def get_messages():
    return jsonify(messages)

@app.post("/messages")
def post_message():
    data = request.get_json(force=True)
    user = data.get("user", "anon")
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Si el mensaje empieza con "clima", el bot responde
    if text.lower().startswith("clima"):
        ciudad = text.split(" ", 1)[1] if " " in text else "Bogota"
        reply = get_weather(ciudad)
        messages.append({
            "user": "BotClima",
            "text": reply,
            "timestamp": datetime.utcnow().isoformat()
        })

    msg = {
        "user": user,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    messages.append(msg)
    return jsonify(msg), 201

@app.get("/")
def root():
    return app.send_static_file("index.html")