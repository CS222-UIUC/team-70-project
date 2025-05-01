import React, { useState, useEffect } from 'react';
import './GuessScoreboard.css';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Access the environment variable

function GuessScoreboard() {
    const [scores, setScores] = useState({}); // State to hold the scores
    const [csrfToken, setCsrfToken] = useState('');

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
        if (!csrfToken) {
            return; // Wait for CSRF token
        }
        const fetchScores = async () => {
            try {
                console.log(`Attempting to Fetch Guess Scoreboard: ${API_BASE_URL}guess_scoreboard/`);
                const response = await fetch(`${API_BASE_URL}guess_scoreboard/`, {
                    method: 'GET', // Specify the method if needed
                    credentials: 'include', // This ensures cookies are sent
                    headers: {
                        'X-CSRFToken': csrfToken,
                    }
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setScores(data.scores); // Assuming the response structure is { scores: { "guess1": score1, "guess2": score2, ... } }

                // Log the number of scores received
                console.log(`Received ${Object.keys(data.scores).length} scores.`);
            } catch (error) {
                console.log(error.message);
            }
        };

        fetchScores(); // Call the fetch function
    }, [csrfToken]); // Runs when CSRF token is updated

    return (
        <div className="guess-scoreboard">
            <div className="scoreboard-title-wrapper">
                <h3>Past Guess Scoreboard</h3>
            </div>
            <div className="divider"></div>
            <div className="scores-list">
                {scores && Object.keys(scores).length > 0 ? ( // Check if scores is not null and has entries
                    Object.entries(scores).map(([guess, score]) => (
                        <div key={guess} className="score-item">
                            <span>{guess}: </span>
                            <span>{score}</span>
                        </div>
                    ))
                ) : (
                    <div>No scores available.</div> // Message when there are no scores
                )}
            </div>
        </div>
    );
}

export default GuessScoreboard;
