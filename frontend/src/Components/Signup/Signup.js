import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Signup.css';

function Signup() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: '',
  });
  const [error, setError] = useState('');
  const [csrfToken, setCsrfToken] = useState('');
  const navigate = useNavigate();

  // Fetch CSRF token -> CSRF token isn't set up to hook into allauth just yet
  useEffect(() => {
    axios.get('http://localhost:8000/accounts/csrf/')
      // eslint-disable-next-line no-unused-vars
      .then(response => {
        const csrfToken = getCookie('csrftoken');
        setCsrfToken(csrfToken);
      })
      .catch(error => {
        console.error('Error fetching CSRF token:', error);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    
    if (formData.password1 !== formData.password2) {
      setError('Passwords do not match');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/accounts/signup/', 
        {
          username: formData.username,
          email: formData.email,
          password1: formData.password1,
          password2: formData.password2,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          withCredentials: true
        }
      );
      
      if (response.status === 200 || response.status === 201) {
        console.log('Signup successful');
        navigate('/login');
      }
    } catch (error) {
      console.error('Signup error:', error.response?.data);
      if (error.response?.data) {
        // Handle specific error messages from Django
        const errorMessages = [];
        for (const key in error.response.data) {
          errorMessages.push(`${key}: ${error.response.data[key].join(' ')}`);
        }
        setError(errorMessages.join('\n'));
      } else {
        setError('An error occurred during signup. Please try again.');
      }
    }
  };

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  // page render function
  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      {error && <div className="error-message" style={{whiteSpace: 'pre-line'}}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password1">Password:</label>
          <input
            type="password"
            id="password1"
            value={formData.password1}
            onChange={(e) => setFormData({...formData, password1: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password2">Confirm Password:</label>
          <input
            type="password"
            id="password2"
            value={formData.password2}
            onChange={(e) => setFormData({...formData, password2: e.target.value})}
            required
          />
        </div>
        <button type="submit">Sign Up</button>
      </form>
      <div className="auth-links">
        Already have an account? <Link to="/login">Login here</Link>
      </div>
    </div>
  );
}

export default Signup;