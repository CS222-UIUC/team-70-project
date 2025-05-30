// import React, { useState, useRef, useEffect } from 'react';
// eslint-disable-next-line no-unused-vars
import { BrowserRouter as Router, Route, Routes, useLocation} from 'react-router';
import './App.css';
import './Components/Keyboard/keyboard.css'; 
import {ProfilePage} from './Components/ProfilePage/ProfilePage';
import IndexPage from './Components/IndexPage/IndexPage';
import Login from './Components/Login/Login';
import Signup from './Components/Signup/Signup';
import { AuthProvider } from './Components/UseAuth';
function App() {
  return (
    <AuthProvider>
    <Router>
      <Routes>
        <Route path="/"         element={ <IndexPage />   } />
        <Route path="/login"    element={ <Login />       } />
        <Route path="/signup"   element={ <Signup />      } />
        <Route path="/profile"  element={ <ProfilePage /> } />
      </Routes>
    </Router>
    </AuthProvider>
  );
}

export default App;