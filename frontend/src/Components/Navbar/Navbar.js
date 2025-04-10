import React from 'react';
import { Link } from 'react-router';
import './Navbar.css';

function Navbar() {
    return (
        <div className="navbar">
            <h3 className="title">Wikipedle</h3>
            <div className="nav-links">
                <Link to="/" className="nav-link">Play</Link>
                <Link to="/signup" className="nav-link">Create account</Link>
                <Link to="/login" className="nav-link">Log in</Link>
                <Link to="/profile" className="nav-link">Profile</Link>
            </div>
        </div>
    );
}

export default Navbar;