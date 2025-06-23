# Entra nella cartella backend
cd backend

# Crea il file requirements se manca
if (-not (Test-Path "requirements.txt")) {
    @"
fastapi
uvicorn[standard]
geopy
python-dotenv
sqlalchemy
scikit-learn
numpy
requests
python-multipart
"@ | Out-File -Encoding utf8 requirements.txt
}

# Installa dipendenze
pip install -r requirements.txt

# Avvia il server
uvicorn main:app --reload --port 8000