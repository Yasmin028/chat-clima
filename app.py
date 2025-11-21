from flask import Flask, request, jsonify
from datetime import datetime
import requests
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, static_folder="static")

OPENWEATHER_KEY = os.environ.get("399edb2f7c72b4688028518a3e182f7d")

# Render te da DATABASE_URL, pero a veces empieza con "postgres://"
# SQLAlchemy necesita "postgresql://"
db_url = os.environ.get("postgresql://chat_p1k4_user:uxOEGpxVvZiqFVmwN2jpWyQj6P7FsC2S@dpg-d4g7bamr433s73ehhhi0-a.oregon-postgres.render.com/chat_p1k4")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))
    text = db.Column(db.String(200))
    city = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
    res = requests.get(url, timeout=5).json()
    return f"{res['main']['temp']} °C, {res['weather'][0]['description']}"

@app.get("/messages")
def get_messages():
    msgs = Message.query.order_by(Message.timestamp.asc()).all()
    return jsonify([{
        "user": m.user,
        "text": m.text,
        "city": m.city,
        "timestamp": m.timestamp.isoformat()
    } for m in msgs])

@app.post("/messages")
def post_message():
    data = request.get_json(force=True)
    user = data.get("user", "anon")
    text = data.get("text", "").strip()
    city = data.get("city", "").strip()

    if not text:
        return jsonify({"error": "Mensaje vacío"}), 400

    msg = Message(user=user, text=text, city=city)
    db.session.add(msg)
    db.session.commit()

    if city:
        clima = get_weather(city)
        bot_msg = Message(user="BotClima", text=f"Clima en {city}: {clima}", city=city)
        db.session.add(bot_msg)
        db.session.commit()

    return jsonify({"user": user, "text": text, "city": city}), 201

@app.get("/")
def root():
    return app.send_static_file("index.html")