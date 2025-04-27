import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './ProfilePage.css';

export function ProfilePage() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [csrfToken, setCsrfToken] = useState('');
    const navigate = useNavigate();

    // Fetch CSRF token
    useEffect(() => {
        axios.get('http://localhost:8000/csrf/', { withCredentials: true })
            .then(response => {
                console.log('CSRF response:', response.data);
                const token = response.data.csrfToken;
                setCsrfToken(token);
                console.log('CSRF token set:', token);
            })
            .catch(error => {
                console.error('Error fetching CSRF token:', error);
            });
    }, []);

    useEffect(() => {
        const fetchProfile = async () => {
            if (!csrfToken) {
                return; // Wait for CSRF token
            }
            
            try {
                const response = await axios.get('http://localhost:8000/profile/', {
                    withCredentials: true,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    }
                });
                setProfile(response.data);
                setLoading(false);
            } catch (err) {
                if (err.response?.status === 401) {
                    navigate('/login');
                } else {
                    setError('Failed to load profile data');
                    console.error('Error:', err);
                }
                setLoading(false);
            }
        };

        fetchProfile();
    }, [navigate, csrfToken]);

    if (loading) {
        return (
            <div className="profile-page">
                <h1>Loading Profile...</h1>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-page">
                <h1>Error</h1>
                <p className="error-message">{error}</p>
            </div>
        );
    }    
        return (
            <div className="profile-page">
                <h1>Profile</h1>
                <div className="profile-info">
                    <div className="user-details">
                        <h2>{profile.username}</h2>
                        <p className="email">{profile.email}</p>
                    </div>
                    <div className="stats-container">
                        <h3>Game Statistics</h3>
                        <div className="stats-table">
                            <div className="stats-row">
                                <div className="stat-cell">
                                    <span className="stat-label">Games Played</span>
                                    <span className="stat-value">{profile.total_games_played}</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Games Won</span>
                                    <span className="stat-value">{profile.total_wins}</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Win Rate</span>
                                    <span className="stat-value">{profile.win_rate}%</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Best Score</span>
                                    <span className="stat-value">{profile.best_score}</span>
                                </div>
                            </div>
                            <div className="stats-row">
                                <div className="stat-cell">
                                    <span className="stat-label">Current Streak</span>
                                    <span className="stat-value">{profile.current_streak}</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Max Streak</span>
                                    <span className="stat-value">{profile.max_streak}</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Average Score</span>
                                    <span className="stat-value">{profile.average_score.toFixed(1)}</span>
                                </div>
                                <div className="stat-cell">
                                    <span className="stat-label">Last Played</span>
                                    <span className="stat-value">
                                        {profile.last_played ? new Date(profile.last_played).toLocaleDateString() : 'Never'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }