import React, { useState, useRef, useEffect } from 'react';
import './IndexPage.css';
import ArticleDisplay from '../ArticleDisplay/ArticleDisplay';
import VirtualKeyboard from '../Keyboard/keyboard.js';

function IndexPage() {
    const [inputValue, setInputValue] = useState("");
    const textInputRef = useRef(null);

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
            case "Enter":
                setInputValue((prev) => prev + "\n");
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
    return (
        <div className = "index-page">
            <div className = "header">
                <h3 className = "title">Wikipedle</h3>
            </div>

            <div className = "game-container">
                <div className = "left-sidebar">
                    <div className = "scoreboard-title-wrapper">
                        <h3>Past Guess Scoreboard</h3>
                    </div>
                    <div className="divider"></div>
                </div>

                <div className = "content">
                    <div className = "input-container-wrapper" onClick={() => textInputRef.current && textInputRef.current.focus()}>
                        <pre>{inputValue}</pre>
                        <textarea
                        ref={textInputRef}
                        value={inputValue}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        className="hidden-textarea"
                        />
                    </div>

                    <div className = "article-display-wrapper">
                        <div className = "fake-navbar">
                            <div className = "left-items">
                                <p className = "bold">Article</p>
                                <p>Talk</p>
                            </div>
                            <div className = "right-items">
                                <p className = "bold">Read</p>
                                <p>View source</p>
                                <p>View history</p>
                                <p>Tools</p>
                            </div>
                        </div>
                        <div className="divider"></div>
                        <p className="blurb">From Wikipedia, the free encyclopedia</p>
                        <ArticleDisplay articleData={{ "main-text" : null }}/>
                    </div>
                </div>

                <div className = "right-sidebar">
                    <div className = "scoreboard-title-wrapper">
                        <h3>Friend Scoreboard</h3>
                    </div>
                    <div className="divider"></div>
                </div>
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