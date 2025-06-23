import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [address, setAddress] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (address.trim()) {
      onSearch(address);
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="Inserisci indirizzo, es. 'Piazza Duomo, Milano'"
      />
      <button type="submit">Cerca Parcheggi</button>
    </form>
  );
};

export default SearchBar;