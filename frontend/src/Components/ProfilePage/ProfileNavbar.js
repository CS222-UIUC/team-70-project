import React from 'react';
import { Link } from 'react-router';
import './ProfileNavbar.css'
function Navbar() {
    return (
        <div className="ProfileNavbar">
            <h3 className="title">Wikipedle</h3>
            <div className="nav-links">
                <Link to="/" className="nav-link">Play</Link>
            </div>
        </div>
    );
}

export default Navbar;