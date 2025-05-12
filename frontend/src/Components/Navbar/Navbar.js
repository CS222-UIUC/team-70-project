import React from 'react';
import { Link, useNavigate } from 'react-router';
import './Navbar.css';
import { useAuth } from '../UseAuth';
import axios from 'axios';
function Navbar({ showProfile }) {
    const { user, setUser } = useAuth();
    const navigate = useNavigate();
    const getCSRFToken = async () => {
        const response = await axios.get('http://localhost:8000/csrf/', { withCredentials: true });
        return response.data.csrfToken;
      };
      const handleLogout = async () => {
        try {
            const csrfToken = await getCSRFToken(); // ✅ fetch it
    
            await axios.post('http://localhost:8000/logout/', {}, {
                headers: {
                    'X-CSRFToken': csrfToken
                },
                withCredentials: true
            });
    
            setUser(null);
            navigate('/');
            window.location.reload(); // Refresh the page to reflect the logout
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };
    return (
        <div className="navbar">
            <h3 className="title">Wikipedle</h3>
            <div className="nav-links">
            <Link to="/" className="nav-link">Play</Link>
                    {user || showProfile ? (
                        <>
                            <Link to="/profile" className="nav-link">Profile</Link>
                            <button onClick={handleLogout} className="nav-link logout-button">Log out</button>
                        </>
                    ) : (
                        <>
                            <Link to="/signup" className="nav-link">Create account</Link>
                            <Link to="/login" className="nav-link">Log in</Link>
                        </>
                    )}
            </div>
        </div>
    );
}

export default Navbar;