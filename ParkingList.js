import React from 'react';

const ParkingList = ({ parkings, onSelect, expanded = false }) => {
  const getAvailabilityClass = (prob) => {
    if (prob > 0.7) return 'high';
    if (prob > 0.4) return 'medium';
    return 'low';
  };

  if (!parkings || parkings.length === 0) {
    return <p>Nessun parcheggio trovato</p>;
  }

  const items = expanded ? parkings : parkings.slice(0, 3);

  return (
    <div className={`parking-list ${expanded ? 'expanded' : ''}`}>
      {items.map((parking, index) => (
        <div 
          key={index} 
          className={`parking-item ${getAvailabilityClass(parking.availability_prob)}`}
          onClick={() => onSelect(parking)}
        >
          <div className="availability-badge">
            {Math.round(parking.availability_prob * 100)}%
          </div>
          <div className="parking-info">
            <h3>{parking.address}</h3>
            <p>Distanza: <strong>{parking.distance.toFixed(2)} km</strong></p>
            <p>
              Disponibilità: 
              <span className="availability-label">
                {Math.round(parking.availability_prob * 100)}%
              </span>
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ParkingList;