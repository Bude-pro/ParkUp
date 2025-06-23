import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const FutureBooking = ({ onPredict }) => {
  const [address, setAddress] = useState('');
  const [datetime, setDatetime] = useState(() => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    return now;
  });
  const [duration, setDuration] = useState(60);

  const handleSubmit = () => {
    if (!address.trim()) {
      alert("Inserisci un indirizzo valido");
      return;
    }
    
    onPredict(address, datetime, duration);
  };

  return (
    <div className="future-booking-form">
      <div className="form-group">
        <label>Indirizzo di destinazione:</label>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Es: Stadio San Siro, Milano"
        />
      </div>
      
      <div className="form-row">
        <div className="form-group">
          <label>Data e Ora:</label>
          <DatePicker
            selected={datetime}
            onChange={setDatetime}
            showTimeSelect
            timeFormat="HH:mm"
            timeIntervals={15}
            timeCaption="Ora"
            dateFormat="dd/MM/yyyy HH:mm"
            minDate={new Date()}
            locale="it"
            className="datetime-picker"
          />
        </div>
        
        <div className="form-group">
          <label>Durata prevista:</label>
          <select 
            value={duration} 
            onChange={(e) => setDuration(Number(e.target.value))}
            className="duration-select"
          >
            <option value="60">1 ora</option>
            <option value="120">2 ore</option>
            <option value="180">3 ore</option>
            <option value="240">4 ore</option>
            <option value="300">5+ ore</option>
          </select>
        </div>
      </div>
      
      <button className="predict-button" onClick={handleSubmit}>
        Trova Parcheggi Previsti
      </button>
    </div>
  );
};

export default FutureBooking;