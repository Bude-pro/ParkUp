import React, { useState } from 'react';

const FeedbackForm = ({ parking, missingFields, onSubmit, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [feedback, setFeedback] = useState({
    free_spots: 0,
    parked_success: true,
    weather: "clear",
    photo_url: ""
  });

  const handleAnswer = (field, value) => {
    setAnswers({ ...answers, [field]: value });
    
    if (currentStep < missingFields.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setCurrentStep('feedback');
    }
  };

  const handleSubmit = () => {
    onSubmit({ 
      ...answers, 
      ...feedback,
      free_spots: Number(feedback.free_spots) || 0
    });
  };

  const renderStep = () => {
    if (currentStep < missingFields.length) {
      const field = missingFields[currentStep];
      
      switch(field) {
        case 'covered':
          return (
            <div className="form-step">
              <h3>Il parcheggio è coperto?</h3>
              <div className="form-buttons">
                <button onClick={() => handleAnswer('covered', true)}>Sì</button>
                <button onClick={() => handleAnswer('covered', false)}>No</button>
              </div>
            </div>
          );
        
        case 'paid':
          return (
            <div className="form-step">
              <h3>È a pagamento?</h3>
              <div className="form-buttons">
                <button onClick={() => handleAnswer('paid', true)}>Sì</button>
                <button onClick={() => handleAnswer('paid', false)}>No</button>
              </div>
            </div>
          );
        
        case 'capacity':
          return (
            <div className="form-step">
              <h3>Quanti posti auto ha circa?</h3>
              <input 
                type="number" 
                min="1"
                placeholder="Es: 50"
                onChange={(e) => handleAnswer('capacity', e.target.value)}
              />
              <button className="next-button" onClick={() => setCurrentStep('feedback')}>Continua</button>
            </div>
          );
      }
    }
    
    return (
      <div className="feedback-step">
        <h3>Conferma la tua sosta</h3>
        
        <div className="form-group">
          <label>Sei riuscito a parcheggiare?</label>
          <div className="form-buttons">
            <button 
              className={feedback.parked_success ? 'active' : ''}
              onClick={() => setFeedback({...feedback, parked_success: true})}
            >
              Sì
            </button>
            <button 
              className={!feedback.parked_success ? 'active' : ''}
              onClick={() => setFeedback({...feedback, parked_success: false})}
            >
              No
            </button>
          </div>
        </div>
        
        <div className="form-group">
          <label>Posti liberi vicino:</label>
          <input 
            type="number" 
            min="0"
            value={feedback.free_spots}
            onChange={(e) => setFeedback({...feedback, free_spots: e.target.value})}
          />
        </div>
        
        <div className="form-group">
          <label>Condizioni meteo:</label>
          <select 
            value={feedback.weather}
            onChange={(e) => setFeedback({...feedback, weather: e.target.value})}
          >
            <option value="clear">Sereno</option>
            <option value="rain">Pioggia</option>
            <option value="snow">Neve</option>
            <option value="fog">Nebbia</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Eventi speciali (opzionale):</label>
          <input 
            type="text"
            placeholder="Es: Concerto, Mercato"
            value={feedback.event_context || ''}
            onChange={(e) => setFeedback({...feedback, event_context: e.target.value})}
          />
        </div>
        
        <div className="form-group">
          <label>Foto (URL opzionale):</label>
          <input 
            type="text"
            placeholder="Incolla URL immagine"
            value={feedback.photo_url}
            onChange={(e) => setFeedback({...feedback, photo_url: e.target.value})}
          />
        </div>
        
        <div className="form-actions">
          <button className="cancel-btn" onClick={onClose}>Annulla</button>
          <button className="submit-btn" onClick={handleSubmit}>Invia Feedback</button>
        </div>
      </div>
    );
  };

  return (
    <div className="feedback-modal">
      <div className="modal-content">
        <h2>{parking.address}</h2>
        {renderStep()}
      </div>
    </div>
  );
};

export default FeedbackForm;