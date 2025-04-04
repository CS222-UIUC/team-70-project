import React, { useState, useEffect } from 'react';
import './FriendScoreboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Access the environment variable

function FriendScoreboard() {
    const [scores, setScores] = useState({}); // State to hold the scores

    useEffect(() => {
        const fetchScores = async () => {
            try {
                console.log(`Attempting to Fetch Friend Scoreboard: ${API_BASE_URL}friend_scoreboard/`);
                const response = await fetch(`${API_BASE_URL}friend_scoreboard/`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setScores(data.scores); // Assuming the response structure is { scores: { "friend1": score1, "friend2": score2, ... } }

                // Log the number of scores received
                console.log(`Received ${Object.keys(data.scores).length} scores.`);
            } catch (error) {
                console.log(error.message);
            }
        };

        fetchScores(); // Call the fetch function
    }, []); // Empty dependency array means this runs once on mount

    return (
        <div className = "friend-scoreboard">
            <div className = "scoreboard-title-wrapper">
                <h3>Friend Scoreboard</h3>
            </div>
            <div className="divider"></div>
            <div className="scores-list">
                {scores && Object.keys(scores).length > 0 ? ( // Check if scores is not null and has entries
                    Object.entries(scores).map(([friend, score]) => (
                        <div key={friend} className="score-item">
                            <span>{friend}: </span>
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

export default FriendScoreboard;