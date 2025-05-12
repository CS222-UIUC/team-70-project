import React, { useState, useRef, useEffect } from 'react';
import './IndexPage.css';
import Navbar from '../Navbar/Navbar';
import GuessScoreboard from '../GuessScoreboard/GuessScoreboard';
import FriendScoreboard from '../FriendScoreboard/FriendScoreboard';
import ArticleDisplay from '../ArticleDisplay/ArticleDisplay';
import VirtualKeyboard from '../Keyboard/keyboard.js';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function IndexPage() {
    const [inputValue, setInputValue] = useState("");
    const textInputRef = useRef(null);
    const [csrfToken, setCsrfToken] = useState('');
    const [finalScore, setFinalScore] = useState("");
    const [finalTitle, setFinalTitle] = useState("");
    const [showModal, setShowModal] = useState(false);
    const [showProfile, setShowProfile] = useState(false);

    // Fetch game over status, score, and title
    useEffect(() => {
        axios.get(`${API_BASE_URL}game_over/`, { withCredentials: true })
            .then(response => {
                console.log('Game over response:', response.data);
                setFinalScore(response.data.score);
                setFinalTitle(response.data.title);
                setShowProfile(true);

                if (response.data.game_over) {
                    setShowModal(true);
                }
            })
            .catch(error => {
                console.error('Error fetching game over status:', error);
                setShowModal(false);
                setFinalScore("");
                setFinalTitle("");
                setShowProfile(false);
            });
    }, []);

    // Modal Component for game over popup
    const Modal = ({ message1, message2, onClose }) => {
        return (
            <div className={`modal-overlay fade-in`}>
                <div className={`modal-content fade-in`}>
                    <h1>Game Over!</h1>
                    <p>{message1}</p>
                    <p>{message2}</p>
                    <button onClick={onClose}>Close</button>
                </div>
            </div>
        );
    };

    const handleCloseModal = () => {
        console.log("Closing modal...");
        setShowModal(false); // Hide the modal after the fade-out animation
    };

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
        if (textInputRef.current) {
          textInputRef.current.focus(); //.focus() sets focus on textboxes
        }
    }, []);
    //cases for keypresses
    const handleKeyPress = (key) => {
        switch (key) {
            case "Backspace":
                setInputValue((prev) => prev.slice(0, -1));
                break;
            case "Space":
                setInputValue((prev) => prev + " ");
                break;
            case "Tab":
                setInputValue((prev) => prev + "\t");
                break;
                break;
            case "Caps":
            case "Shift":
            case "Ctrl":
            case "Alt":
            // These keys don't add text
                break;
            default:
                setInputValue((prev) => prev + key);
                break;
        }
        // Refocus the hidden input after virtual key press
        if (textInputRef.current) {
            textInputRef.current.focus();
        }
    };
    
    const handleInputChange = (e) => {
        setInputValue(e.target.value);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Tab") {
            e.preventDefault();
            setInputValue((prev) => prev + "\t");
        }
    };

    const handleSubmit = () => {
        // Implement the submit logic here
        console.log("Submitted input:", inputValue);

        // Make POST request to API with guess
        const trimmedInputValue = inputValue.trim();
        if (trimmedInputValue !== "") {
            const url = `${API_BASE_URL}process_guess/`;
            const data = { 'guess': trimmedInputValue };
            fetch(url, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                window.location.reload(); // Reload page 
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }

        // Reset values in the input box and hidden text area
        setInputValue("");
        if (textInputRef.current) {
            textInputRef.current.value = "";
        }
    };

    return (
        <div className = "index-page">
            <Navbar showProfile={showProfile} />

            {showModal && <Modal 
                message1={`The Article Title Was: ${finalTitle}`} 
                message2={`Your Final Score Was: ${finalScore}`} 
                onClose={handleCloseModal} 
            />}

            <div className = "game-container">
                <GuessScoreboard />

                <div className = "content">
                    <div className = "input-container-wrapper" onClick={() => textInputRef.current && textInputRef.current.focus()}>
                        <div className="text-container">
                            <pre>{inputValue}</pre>
                            <textarea
                            ref={textInputRef}
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            className="hidden-textarea"
                            />
                        </div>
                        
                        <div className="submit-button-container">
                            <button className = "submit-button" onClick={handleSubmit}>Submit &#8594;</button>
                        </div>
                    </div>

                    <div className = "article-display-wrapper">
                        <div className = "fake-navbar">
                            <div className = "fn-left-items">
                                <p className = "bold">Article</p>
                                <p>Talk</p>
                            </div>
                            <div className = "fn-right-items">
                                <p className = "bold">Read</p>
                                <p>View source</p>
                                <p>View history</p>
                                <p>Tools</p>
                            </div>
                        </div>
                        <div className="divider"></div>
                        <p className="blurb">From Wikipedia, the free encyclopedia</p>
                        <ArticleDisplay />
                    </div>
                </div>

                <FriendScoreboard />
            </div>

            <div className = "footer">
                <div className = "keyboard-wrapper">
                    <div className="keyboard-container"> 
                        <VirtualKeyboard onKeyPress={handleKeyPress} />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default IndexPage;