import { useState,useEffect } from 'react'
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './App.css'
import './Pages/LoginSignup'
import LoginSignup from './Pages/LoginSignup'
import Home from './Pages/Home';




function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('auth-token');
    if (token) {
      setIsLoggedIn(true);
    }
  });



  return (
    <Router>
      <div className="App">
        <Routes>
        <Route path='/' element={<LoginSignup/>}/>
        <Route path='/home' element={<Home/>}/>
          <Route path="/login" element={<LoginSignup />} />
          <Route path="/signup" element={<LoginSignup  />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

