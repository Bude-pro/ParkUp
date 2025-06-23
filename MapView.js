import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix per le icone marker
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapView = ({ userLocation, parkings, onSelect, futureMode = false }) => {
  const getMarkerColor = (availability) => {
    if (availability > 0.7) return 'green';
    if (availability > 0.4) return 'orange';
    return 'red';
  };

  const getPosition = () => {
    if (userLocation) return [userLocation.lat, userLocation.lng];
    if (parkings?.length > 0) return [parkings[0].latitude, parkings[0].longitude];
    return [45.4642, 9.1900]; // Default Milano
  };

  return (
    <MapContainer 
      center={getPosition()} 
      zoom={15} 
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {userLocation && (
        <Marker position={[userLocation.lat, userLocation.lng]}>
          <Popup>La tua posizione</Popup>
        </Marker>
      )}
      
      {parkings?.map(parking => (
        <Marker 
          key={parking.id} 
          position={[parking.latitude, parking.longitude]}
          eventHandlers={{ click: () => onSelect(parking) }}
          icon={L.divIcon({
            className: 'custom-marker',
            html: `<div style="background:${getMarkerColor(parking.availability_prob)}; 
                    width: 28px; height: 28px; border-radius: 50%; border: 2px solid white"></div>`
          })}
        >
          <Popup>
            <strong>{parking.address}</strong><br/>
            {futureMode ? (
              <>
                Data: {new Date(parking.target_time).toLocaleString('it-IT')}<br/>
                Disponibilità prevista: {Math.round(parking.availability_prob * 100)}%
              </>
            ) : (
              <>
                Distanza: {parking.distance?.toFixed(2) || 'N/A'} km<br/>
                Disponibilità: {Math.round(parking.availability_prob * 100)}%
              </>
            )}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView;