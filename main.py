import sqlite3
import math
import datetime
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from geopy.geocoders import Nominatim
from typing import Optional
import calendar
import pytz

app = FastAPI()

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelli dati
class ParkingRequest(BaseModel):
    address: str

class FutureParkingRequest(BaseModel):
    address: str
    target_datetime: datetime.datetime
    duration_minutes: int = 60

class ParkingCreate(BaseModel):
    latitude: float
    longitude: float
    address: str
    covered: Optional[bool] = None
    paid: Optional[bool] = None
    capacity: Optional[int] = None
    pricing_info: Optional[str] = None

class FeedbackCreate(BaseModel):
    parking_id: str
    free_spots: int
    parked_success: bool
    weather: Optional[str] = None
    event_context: Optional[str] = None
    photo_url: Optional[str] = None

# Inizializzazione
geolocator = Nominatim(user_agent="parcheggiml_full_v1")
DB_PATH = "ai_parking.db"
TIMEZONE = pytz.timezone("Europe/Rome")

# Connessione DB
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS parkings (
        id TEXT PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        address TEXT NOT NULL,
        covered INTEGER,
        paid INTEGER,
        capacity INTEGER,
        pricing_info TEXT,
        last_updated TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parking_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        free_spots INTEGER,
        parked_success INTEGER,
        weather TEXT,
        event_context TEXT,
        photo_url TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS historical_data (
        parking_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        availability REAL,
        PRIMARY KEY (parking_id, timestamp)
    )''')
    conn.commit()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

# Funzioni IA
def get_time_factor(target_time):
    hour = target_time.hour
    if 7 <= hour < 12: return 0.6  # Mattina - alta occupazione
    elif 12 <= hour < 15: return 0.4  # Pranzo - media occupazione
    elif 15 <= hour < 19: return 0.8  # Pomeriggio - alta disponibilità
    else: return 0.3  # Notte - bassa occupazione

def is_holiday(date):
    italian_holidays = [
        datetime.date(date.year, 1, 1),   # Capodanno
        datetime.date(date.year, 1, 6),   # Epifania
        datetime.date(date.year, 4, 25),  # Liberazione
        datetime.date(date.year, 5, 1),   # Lavoro
        datetime.date(date.year, 6, 2),   # Repubblica
        datetime.date(date.year, 8, 15),  # Ferragosto
        datetime.date(date.year, 11, 1),  # Ognissanti
        datetime.date(date.year, 12, 8),  # Immacolata
        datetime.date(date.year, 12, 25), # Natale
        datetime.date(date.year, 12, 26)  # Santo Stefano
    ]
    return date.date() in italian_holidays

def get_historical_availability(parking_id, target_time):
    conn = get_db()
    cur = conn.cursor()
    time_match = f"{target_time.month:02d}-{target_time.day:02d} {target_time.hour:02d}"
    
    cur.execute("""
        SELECT AVG(availability)
        FROM historical_data
        WHERE parking_id = ? 
        AND SUBSTR(timestamp, 6, 8) = ?
    """, (parking_id, time_match))
    
    result = cur.fetchone()
    return result[0] if result and result[0] else 0.5

def get_gps_density(lat, lng, radius=0.5):
    # In produzione: integrerebbe con API GPS reali
    return 0.7  # Valore simulato

def get_weather_forecast(lat, lng, target_time):
    # Simulazione - in produzione userebbe OpenWeatherMap
    return {"condition": "sunny", "impact": 1.0}

def get_local_events(lat, lng, radius=2):
    # Simulazione - in produzione userebbe API eventi
    return ["Concerto"] if "stadio" in lng else []

def get_pricing_impact(parking_id, target_time):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT paid, pricing_info FROM parkings WHERE id = ?", (parking_id,))
    result = cur.fetchone()
    
    if not result or not result[0]:
        return 1.0
    
    # Logica tariffaria dinamica
    hour = target_time.hour
    is_peak = 8 <= hour < 19
    return 0.6 if is_peak else 0.9

def get_parking_coords(parking_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude FROM parkings WHERE id = ?", (parking_id,))
    return cur.fetchone()

def calculate_availability(parking_id, target_time=None):
    if not target_time:
        target_time = datetime.datetime.now(TIMEZONE)
    else:
        target_time = target_time.astimezone(TIMEZONE)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT covered, paid FROM parkings WHERE id = ?", (parking_id,))
    parking_data = cur.fetchone()
    
    if not parking_data:
        return 0.5
    
    covered, paid = parking_data
    coords = get_parking_coords(parking_id)
    
    if not coords:
        return 0.5
    
    lat, lng = coords
    
    # Calcolo fattori
    weather = get_weather_forecast(lat, lng, target_time)
    events = get_local_events(lat, lng)
    
    factors = {
        'time': (get_time_factor(target_time), 0.15),
        'holiday': (0.4 if is_holiday(target_time) else 1.0, 0.1),
        'history': (get_historical_availability(parking_id, target_time), 0.25),
        'gps': (get_gps_density(lat, lng), 0.15),
        'weather': (weather['impact'], 0.1),
        'events': (0.5 if events else 1.0, 0.1),
        'pricing': (get_pricing_impact(parking_id, target_time), 0.1),
        'covered': (0.9 if covered else 1.0, 0.05)
    }
    
    # Calcolo ponderato
    total_weight = sum(weight for _, weight in factors.values())
    availability = sum(factor * weight for factor, weight in factors.values()) / total_weight
    
    return max(0.1, min(0.99, availability))

# Endpoint principali
@app.post("/find-parking")
async def find_parking(request: ParkingRequest):
    try:
        location = geolocator.geocode(request.address)
        if not location:
            return {"error": "Indirizzo non trovato"}
        
        user_lat, user_lon = location.latitude, location.longitude
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM parkings")
        parkings = cur.fetchall()
        
        results = []
        for p in parkings:
            dist = haversine(user_lat, user_lon, p[1], p[2])
            avail_prob = calculate_availability(p[0])
            
            results.append({
                "id": p[0],
                "address": p[3],
                "latitude": p[1],
                "longitude": p[2],
                "distance": dist,
                "availability_prob": avail_prob,
                "covered": bool(p[4]),
                "paid": bool(p[5]),
                "capacity": p[6]
            })
        
        results.sort(key=lambda x: (-x['availability_prob'], x['distance']))
        return {
            "user_location": {"lat": user_lat, "lng": user_lon},
            "top_parkings": results[:3],
            "all_parkings": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-future-parking")
async def predict_future_parking(request: FutureParkingRequest):
    location = geolocator.geocode(request.address)
    if not location:
        raise HTTPException(status_code=404, detail="Indirizzo non trovato")
    
    target_time = request.target_datetime.astimezone(TIMEZONE)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parkings")
    parkings = cur.fetchall()
    
    results = []
    for p in parkings:
        dist = haversine(location.latitude, location.longitude, p[1], p[2])
        avail_prob = calculate_availability(p[0], target_time)
        
        results.append({
            "id": p[0],
            "address": p[3],
            "latitude": p[1],
            "longitude": p[2],
            "distance": dist,
            "availability_prob": avail_prob,
            "target_time": target_time.isoformat(),
            "covered": bool(p[4]),
            "paid": bool(p[5]),
            "capacity": p[6]
        })
    
    results.sort(key=lambda x: (-x['availability_prob'], x['distance']))
    return {"parkings": results[:3]}

@app.post("/register-parking")
async def register_parking(parking: ParkingCreate):
    conn = get_db()
    cur = conn.cursor()
    pid = f"park_{uuid.uuid4().hex[:8]}"
    
    cur.execute('''
        INSERT INTO parkings 
        (id, latitude, longitude, address, covered, paid, capacity, pricing_info, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pid,
        parking.latitude,
        parking.longitude,
        parking.address,
        1 if parking.covered else 0 if parking.covered is not None else None,
        1 if parking.paid else 0 if parking.paid is not None else None,
        parking.capacity,
        parking.pricing_info,
        datetime.datetime.now(TIMEZONE).isoformat()
    ))
    
    conn.commit()
    return {"id": pid, "status": "registered"}

@app.post("/submit-feedback")
async def submit_feedback(feedback: FeedbackCreate):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO feedbacks 
        (parking_id, timestamp, free_spots, parked_success, weather, event_context, photo_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        feedback.parking_id,
        datetime.datetime.now(TIMEZONE).isoformat(),
        feedback.free_spots,
        1 if feedback.parked_success else 0,
        feedback.weather,
        feedback.event_context,
        feedback.photo_url
    ))
    
    conn.commit()
    
    # Aggiorna dati storici
    try:
        avail = 1.0 if feedback.parked_success else 0.0
        cur.execute('''
            INSERT OR REPLACE INTO historical_data 
            (parking_id, timestamp, availability)
            VALUES (?, ?, ?)
        ''', (feedback.parking_id, datetime.datetime.now(TIMEZONE).isoformat(), avail))
        conn.commit()
    except Exception as e:
        print(f"Errore aggiornamento storico: {e}")
    
    return {"status": "success"}

@app.get("/missing-info/{parking_id}")
async def get_missing_info(parking_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT covered, paid, capacity FROM parkings WHERE id = ?", (parking_id,))
    result = cur.fetchone()
    
    if not result:
        return {"missing_fields": []}
    
    missing = []
    if result[0] is None: missing.append("covered")
    if result[1] is None: missing.append("paid")
    if result[2] is None: missing.append("capacity")
    
    return {"missing_fields": missing}

@app.get("/")
def health_check():
    return {"status": "active", "service": "ParcheggiML Backend"}

# Avvia tutto
init_db()