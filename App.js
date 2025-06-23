import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchBar from './components/SearchBar';
import MapView from './components/MapView';
import ParkingList from './components/ParkingList';
import FeedbackForm from './components/FeedbackForm';
import FutureBooking from './components/FutureBooking';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function App() {
  const [view, setView] = useState('current');
  const [searchResults, setSearchResults] = useState(null);
  const [futureResults, setFutureResults] = useState(null);
  const [selectedParking, setSelectedParking] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [missingInfo, setMissingInfo] = useState([]);

  const searchParking = async (address) => {
    try {
      const response = await axios.post(`${API_URL}/find-parking`, { address });
      setSearchResults(response.data);
      setView('current');
    } catch (error) {
      alert('Errore ricerca: ' + (error.response?.data?.error || error.message));
    }
  };

  const predictFutureParking = async (address, datetime, duration) => {
    try {
      const response = await axios.post(`${API_URL}/predict-future-parking`, {
        address,
        target_datetime: datetime.toISOString(),
        duration_minutes: duration
      });
      
      setFutureResults(response.data.parkings);
      setView('future');
    } catch (error) {
      alert('Errore previsione: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleParkingSelect = async (parking) => {
    setSelectedParking(parking);
    try {
      const response = await axios.get(`${API_URL}/missing-info/${parking.id}`);
      setMissingInfo(response.data.missing_fields);
      setShowFeedback(true);
    } catch (error) {
      console.error('Errore dati mancanti:', error);
      setShowFeedback(true);
    }
  };

  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      await axios.post(`${API_URL}/submit-feedback`, {
        ...feedbackData,
        parking_id: selectedParking.id
      });
      alert('Feedback inviato con successo!');
      setShowFeedback(false);
    } catch (error) {
      alert('Errore invio feedback: ' + error.message);
    }
  };

  const getAvailabilityClass = (prob) => {
    if (prob > 0.7) return 'high';
    if (prob > 0.4) return 'medium';
    return 'low';
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🚗 ParcheggiML</h1>
        <div className="view-selector">
          <button 
            className={view === 'current' ? 'active' : ''}
            onClick={() => setView('current')}
          >
            Ricerca Corrente
          </button>
          <button 
            className={view === 'future' ? 'active' : ''}
            onClick={() => setView('future')}
          >
            Prenotazione Futura
          </button>
        </div>
        
        {view === 'current' ? (
          <SearchBar onSearch={searchParking} />
        ) : (
          <FutureBooking onPredict={predictFutureParking} />
        )}
      </header>

      {view === 'current' && searchResults && (
        <div className="main-content">
          <div className="map-section">
            <MapView 
              userLocation={searchResults.user_location} 
              parkings={searchResults.all_parkings} 
              onSelect={handleParkingSelect}
            />
          </div>
          
          <div className="results-section">
            <h2>Migliori parcheggi</h2>
            <ParkingList 
              parkings={searchResults.top_parkings} 
              onSelect={handleParkingSelect} 
            />
            
            <h2>Tutti i parcheggi</h2>
            <ParkingList 
              parkings={searchResults.all_parkings} 
              onSelect={handleParkingSelect}
              expanded={true}
            />
          </div>
        </div>
      )}
      
      {view === 'future' && futureResults && (
        <div className="future-results">
          <div className="prediction-header">
            <h2>Previsione per il {new Date(futureResults[0]?.target_time).toLocaleString('it-IT', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}</h2>
            <p>Durata prevista: {futureResults[0]?.duration_minutes || 60} minuti</p>
          </div>
          
          <div className="map-section">
            <MapView 
              parkings={futureResults}
              onSelect={handleParkingSelect}
              futureMode={true}
            />
          </div>
          
          <div className="predictions-section">
            <h3>Migliori opzioni:</h3>
            <div className="predictions-grid">
              {futureResults.map((parking, index) => (
                <div 
                  key={index} 
                  className={`prediction-card ${getAvailabilityClass(parking.availability_prob)}`}
                  onClick={() => handleParkingSelect(parking)}
                >
                  <div className="availability-badge">
                    {Math.round(parking.availability_prob * 100)}%
                  </div>
                  <h3>{parking.address}</h3>
                  <p>Distanza: <strong>{parking.distance.toFixed(2)} km</strong></p>
                  <p>Coperto: {parking.covered ? 'Sì' : 'No'}</p>
                  <p>Posti stimati: {parking.capacity || 'N/A'}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {!searchResults && view === 'current' && (
        <div className="welcome-message">
          <p>Cerca un indirizzo per trovare parcheggi disponibili!</p>
          <div className="sample-addresses">
            <button onClick={() => searchParking("Piazza Duomo, Milano")}>Milano</button>
            <button onClick={() => searchParking("Colosseo, Roma")}>Roma</button>
            <button onClick={() => searchParking("Piazza del Plebiscito, Napoli")}>Napoli</button>
          </div>
        </div>
      )}
      
      {showFeedback && selectedParking && (
        <FeedbackForm 
          parking={selectedParking}
          missingFields={missingInfo}
          onSubmit={handleFeedbackSubmit}
          onClose={() => setShowFeedback(false)}
        />
      )}
    </div>
  );
}

export default App;