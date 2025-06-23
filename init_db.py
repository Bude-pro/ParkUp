import sqlite3

def init_database():
    conn = sqlite3.connect('ai_parking.db')
    c = conn.cursor()
    
    # Tabella parcheggi
    c.execute('''CREATE TABLE IF NOT EXISTS parkings (
        id TEXT PRIMARY KEY,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        address TEXT NOT NULL,
        covered INTEGER,  -- 0/1
        paid INTEGER,     -- 0/1
        capacity INTEGER,
        last_updated TEXT
    )''')
    
    # Tabella feedback
    c.execute('''CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parking_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        free_spots INTEGER,
        parked_success INTEGER,  -- 0/1
        weather TEXT,
        FOREIGN KEY(parking_id) REFERENCES parkings(id)
    )''')
    
    # Inserisci dati di esempio (solo per test)
    sample_data = [
        ('park1', 45.4642, 9.1900, 'Piazza Duomo, Milano', 1, 1, 100, '2023-10-01'),
        ('park2', 45.4650, 9.1915, 'Galleria Vittorio Emanuele', 0, 1, 50, '2023-10-01'),
        ('park3', 45.4630, 9.1880, 'Via Torino', 1, 0, 30, '2023-10-01')
    ]
    
    c.executemany('''INSERT OR IGNORE INTO parkings VALUES (?,?,?,?,?,?,?)''', sample_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database inizializzato con successo!")