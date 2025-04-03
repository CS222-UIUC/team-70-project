import React, { useState, useEffect } from 'react';
import './ArticleDisplay.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; // Access the environment variable

function ArticleDisplay() {
    const [article, setArticle] = useState({}); // State to hold the article

    useEffect(() => {
        const fetchScores = async () => {
            try {
                console.log(`Attempting to Fetch Guess Scoreboard: ${API_BASE_URL}scrambled_article/`);
                const response = await fetch(`${API_BASE_URL}scrambled_article/`);
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

        fetchScores(); // Call the fetch function
    }, []); // Empty dependency array means this runs once on mount

    // Default Lorem Ipsum text
    const defaultText = `
    Lorem ipsum (/ˌlɔː.rəm ˈɪp.səm/ LOR-əm IP-səm) is a dummy or placeholder text commonly used in graphic design, publishing, and web development. Its purpose is to permit a page layout to be designed, independently of the copy that will subsequently populate it, or to demonstrate various fonts of a typeface without meaningful text that could be distracting. \n

    Lorem ipsum is typically a corrupted version of De finibus bonorum et malorum, a 1st-century BC text by the Roman statesman and philosopher Cicero, with words altered, added, and removed to make it nonsensical and improper Latin. The first two words themselves are a truncation of dolorem ipsum ("pain itself"). \n

    Versions of the Lorem ipsum text have been used in typesetting at least since the 1960s, when it was popularized by advertisements for Letraset transfer sheets.[1] Lorem ipsum was introduced to the digital world in the mid-1980s, when Aldus employed it in graphic and word-processing templates for its desktop publishing program PageMaker. Other popular word processors, including Pages and Microsoft Word, have since adopted Lorem ipsum,[2] as have many LaTeX packages,[3][4][5] web content managers such as Joomla! and WordPress, and CSS libraries such as Semantic UI.

    A common form of Lorem ipsum reads:

    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
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