import sqlite3
import datetime
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def predict_availability(parking_id):
    conn = sqlite3.connect('ai_parking.db')
    cursor = conn.cursor()
    
    # Recupera feedback storici
    cursor.execute("SELECT * FROM feedbacks WHERE parking_id = ?", (parking_id,))
    feedbacks = cursor.fetchall()
    
    if not feedbacks:
        return 0.7  # Valore di default
    
    # Calcola features
    now = datetime.datetime.now()
    hour = now.hour
    weekday = now.weekday()
    
    # Dummy features (da integrare con API esterne)
    good_weather = 1
    local_events = 0
    
    # Modello di esempio
    model = RandomForestRegressor(n_estimators=100)
    X = np.array([[hour, weekday, good_weather, local_events]])
    
    # Addestramento su dati fittizi
    X_train = np.array([
        [8, 0, 1, 0],
        [12, 2, 1, 0],
        [18, 4, 0, 1],
        [10, 5, 1, 0]
    ])
    y_train = np.array([0.2, 0.6, 0.1, 0.8])
    model.fit(X_train, y_train)
    
    return max(0, min(1, model.predict(X)[0]))