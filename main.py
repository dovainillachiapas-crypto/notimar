import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from twilio.rest import Client
from datetime import datetime, timedelta
from sqlalchemy import func
from database import SessionLocal, Incident, init_db
from classifier import classify

app = FastAPI()
templates = Jinja2Templates(directory="templates")
init_db()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

municipality_coords = {
    "Zihuatanejo Región": [17.6436, -101.5510],
}

def fetch_news():
    KEYWORDS = '"homicidio" OR "asalto" OR "robo de vehículo" OR "ejecutado" OR "ataque armado"'
    ZONA = '"Zihuatanejo" OR "Ixtapa" OR "Petatlán" OR "La Unión" OR "Tecpan"'

    url = f"https://newsapi.org/v2/everything?q=({KEYWORDS}) AND ({ZONA})&language=es&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    return response.get("articles", [])

def send_whatsapp(message):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )

@app.get("/run")
def run_notimar():
    db = SessionLocal()
    articles = fetch_news()
    new_events = []

    for article in articles:
        exists = db.query(Incident).filter(Incident.title == article["title"]).first()
        if not exists:
            level = classify(article["title"])
            incident = Incident(
                title=article["title"],
                municipality="Zihuatanejo Región",
                level=level,
                url=article["url"]
            )
            db.add(incident)
            db.commit()
            new_events.append(f"{level} - {article['title']}")

    if new_events:
        message = "🚨 NOTIMAR ALERTA\n\n" + "\n".join(new_events[:5])
        send_whatsapp(message)

    return {"status": "ok"}
