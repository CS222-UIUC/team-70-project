import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ArticleDisplay.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Access the environment variable

function ArticleDisplay() {
    const [article, setArticle] = useState({}); // State to hold the article
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
        const fetchArticle = async () => {
            if (!csrfToken) {
                return; // Wait for CSRF token
            }

            try {
                console.log(`Attempting to Fetch Article: ${API_BASE_URL}scrambled_article/`);
                const response = await fetch(`${API_BASE_URL}scrambled_article/`, {
                    method: 'GET', // Specify the method if needed
                    credentials: 'include', // This ensures cookies are sent
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    }
                });
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setArticle(data.article); // Assuming form {"article" : { "main-text" : text, "image-url" : text ...}}

                // Log the number of scores received
                console.log(`Received ${Object.keys(data.article).length} article parameters.`);
            } catch (error) {
                console.log(error.message);
            }
        };

        fetchArticle(); // Call the fetch function
    }, [csrfToken]); // Runs when CSRF token is updated

    // Default Lorem Ipsum text
    const defaultText = `
    Loading Article Data...

    Please make sure you are logged in.

    Reload if the page continues to not respond.
    `;

    // Get the main text or use the default
    const mainText = article["main-text"] || defaultText;
    // Split the main text into paragraphs based on newlines
    const paragraphs = mainText.split('\n');

    // Get the header and text if it exists
    const header = article["header"] || null;
    const headerText= article["header-text"] || null;
    const headerParagraphs = headerText ? headerText.split('\n') : [];

    // Get the image if it exists
    const imgUrl = article["image-url"] || null;
    const imgTitle = article["image-title"] || null;
    const imgCaptions = article["captions"] || {};

    return (
        <div className="article-display">
            <div className="article-text-wrapper">
                {paragraphs.map((paragraph, index) => (
                    <p key={index} className="article-text">{paragraph}</p>
                ))}
                {header && <h2>{header}</h2>}
                {headerParagraphs.map((paragraph, index) => (
                    <p key={index} className="article-text">{paragraph}</p>
                ))}
            </div>
            {imgUrl && <div className="article-image-wrapper">
                <div className="image-box">
                    {imgTitle && <h3>{imgTitle}</h3>}
                    <img src={imgUrl} alt={imgTitle} className="article-image"/>
                    {Object.keys(imgCaptions).length > 0 && (
                        <div>
                            {Object.entries(imgCaptions).map(([key, caption]) => (
                                <p key={key} className="caption">{caption}</p>
                            ))}
                        </div>
                    )}
                </div>
            </div>}
        </div>
    );
}

export default ArticleDisplay;