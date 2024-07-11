

import React, { useState } from 'react';
import './CSS/homePage.css';

const Home = () => {
  const [itemName, setItemName] = useState('');
  const [itemPrice, setItemPrice] = useState('');

  const addItem = async () => {
    const cleanedItemName = itemName.trim().toLowerCase();
    const itemData = { name: cleanedItemName, price: itemPrice };
    const token = localStorage.getItem('auth-token');
    let responseData;

    await fetch('http://localhost:4000/add-item', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(itemData),
    })
      .then((resp) => resp.json())
      .then((data) => responseData = data);

    if (responseData.success) {
      alert('Item added successfully');
    } else {
      alert(responseData.errors);
    }
  };

  const onLogout = () => {
    // Clear the authentication token
    localStorage.removeItem('auth-token');
    
    // Redirect to the login page
    window.location.replace("/login");
  };

  return (
    <div className="home">
      <h1>Admin Home Page</h1>
      <div className="add-item-form">
        <input
          type="text"
          placeholder="Item Name"
          value={itemName}
          onChange={(e) => setItemName(e.target.value)}
        />
        <input
          type="number"
          placeholder="Item Price"
          value={itemPrice}
          onChange={(e) => setItemPrice(e.target.value)}
        />
        <button onClick={addItem}>Add Item</button>
        <button onClick={onLogout}>Logout</button>
      </div>
    </div>
  );
};

export default Home;

