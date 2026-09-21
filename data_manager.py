import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
POLLS_FILE = os.path.join(DATA_DIR, "polls.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def load_events():
    ensure_data_dir()
    if not os.path.exists(EVENTS_FILE):
        initial_events = [
            {
                "id": "1",
                "title": "Treino Noturno de Terça",
                "type": "Treino Semanal",
                "date": "2026-09-22",
                "time": "19:30",
                "location": "Parque da Cidade",
                "distance": "8 km",
                "description": "Ritmo moderado com aquecimento e séries curtas no final."
            },
            {
                "id": "2",
                "title": "Treino Longo de Fim de Semana",
                "type": "Treino Longo",
                "date": "2026-09-26",
                "time": "08:30",
                "location": "Marginal Fluvial",
                "distance": "16 km",
                "description": "Ritmo confortável (Z2) com abastecimento aos 8km."
            }
        ]
        save_events(initial_events)
        return initial_events
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_events(events):
    ensure_data_dir()
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

def load_polls():
    ensure_data_dir()
    if not os.path.exists(POLLS_FILE):
        initial_polls = [
            {
                "id": "1",
                "question": "Qual o melhor dia para o Treino Longo desta semana?",
                "options": [
                    {"text": "Sábado às 08:30", "votes": 4},
                    {"text": "Domingo às 09:00", "votes": 7},
                    {"text": "Domingo às 08:00", "votes": 2}
                ],
                "active": True,
                "created_at": "2026-09-21"
            }
        ]
        save_polls(initial_polls)
        return initial_polls
    try:
        with open(POLLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_polls(polls):
    ensure_data_dir()
    with open(POLLS_FILE, "w", encoding="utf-8") as f:
        json.dump(polls, f, indent=2, ensure_ascii=False)

