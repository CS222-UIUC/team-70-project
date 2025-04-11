import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router'; // Import MemoryRouter
import '@testing-library/jest-dom';
import IndexPage from '../Components/IndexPage/IndexPage.js';
import Navbar from '../Components/Navbar/Navbar.js';
import GuessScoreboard from '../Components/GuessScoreboard/GuessScoreboard.js';
import FriendScoreboard from '../Components/FriendScoreboard/FriendScoreboard.js';
import ArticleDisplay from '../Components/ArticleDisplay/ArticleDisplay.js';
import VirtualKeyboard from '../Components/Keyboard/keyboard.js';

// DEFAULT RENDERING TESTS
test('default rendering navbar', () => {
    render(
        <MemoryRouter>
            <Navbar />
        </MemoryRouter>
    );
    expect(screen.getByText(/Wikipedle/i)).toBeInTheDocument();
    expect(screen.getByText(/Play/i)).toBeInTheDocument();
    expect(screen.getByText(/Create account/i)).toBeInTheDocument();
    expect(screen.getByText(/Log in/i)).toBeInTheDocument();
    expect(screen.getByText(/Profile/i)).toBeInTheDocument();
});

test('default rendering guess scoreboard', () => {
    render(<GuessScoreboard />);
    expect(screen.getByText(/Past Guess Scoreboard/i)).toBeInTheDocument();
    expect(screen.getByText(/No scores available./i)).toBeInTheDocument();
});

test('default rendering friend scoreboard', () => {
    render(<FriendScoreboard />);
    expect(screen.getByText(/Friend Scoreboard/i)).toBeInTheDocument();
    expect(screen.getByText(/No scores available./i)).toBeInTheDocument();
});

test('default rendering article display', () => {
    render(<ArticleDisplay />);
    const Lorem = screen.getAllByText(/Lorem ipsum/i);
    expect(Lorem.length).toBeGreaterThan(0);
})

test('default rendering keyboard', () => {
    render(<VirtualKeyboard />);
    const A = screen.getAllByText(/A/);
    expect(A.length).toBeGreaterThan(0);
    const M = screen.getAllByText(/M/);
    expect(M.length).toBeGreaterThan(0);
    const S = screen.getAllByText(/S/);
    expect(S.length).toBeGreaterThan(0);
    expect(screen.getByText(/Backspace/)).toBeInTheDocument();
    expect(screen.getByText(/Enter/)).toBeInTheDocument();
    expect(screen.getByText(/Space/)).toBeInTheDocument();
});

test('default rendering index page', () => {
    const { container } = render(
        <MemoryRouter>
            <IndexPage />
        </MemoryRouter>
    );
    const fakeNav = container.getElementsByClassName("fake-navbar")[0];
    expect(fakeNav).toHaveTextContent(/Article/i);
    expect(fakeNav).toHaveTextContent(/Talk/i);
    expect(fakeNav).toHaveTextContent(/Read/i);
    expect(fakeNav).toHaveTextContent(/View source/i);
    expect(fakeNav).toHaveTextContent(/View history/i);
    expect(fakeNav).toHaveTextContent(/Tools/i);
});

// MOCK FETCH TESTS
global.fetch = jest.fn();

describe('GuessScoreboard Component', () => {
    afterEach(() => {
        jest.clearAllMocks(); // Clear mocks after each test
    });

    test('renders scores when fetch is successful', async () => {
        // Mock successful fetch response
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                scores: {
                    guess1: 10,
                    guess2: 20,
                },
            }),
        });

        render(<GuessScoreboard />);

        // Wait for the scores to be displayed
        await waitFor(() => {
            expect(screen.getByText(/guess1:/i)).toBeInTheDocument();
            expect(screen.getByText(/10/i)).toBeInTheDocument();
            expect(screen.getByText(/guess2:/i)).toBeInTheDocument();
            expect(screen.getByText(/20/i)).toBeInTheDocument();
        });
    });

    test('renders no scores available message when fetch returns empty scores', async () => {
        // Mock fetch response with empty scores
        fetch.mockResolvedValueOnce({
            ok: true,
        });

        render(<GuessScoreboard />);

        // Wait for the no scores message to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument();
        });
    });

    test('renders no scores available message when response is not ok', async () => {
        // Mock fetch response with empty scores
        fetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({
                scores: {},
            }),
        });

        render(<GuessScoreboard />);

        // Wait for the no scores message to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument();
        });
    });

    test('handles fetch error gracefully', async () => {
        // Mock fetch to simulate an error
        fetch.mockRejectedValueOnce(new Error('Network error'));

        render(<GuessScoreboard />);

        // Wait for the error handling (if any) to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument(); // Assuming it falls back to this message
        });
    });
});

describe('FriendScoreboard Component', () => {
    afterEach(() => {
        jest.clearAllMocks(); // Clear mocks after each test
    });

    test('renders scores when fetch is successful', async () => {
        // Mock successful fetch response
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                scores: {
                    guess1: 10,
                    guess2: 20,
                },
            }),
        });

        render(<FriendScoreboard />);

        // Wait for the scores to be displayed
        await waitFor(() => {
            expect(screen.getByText(/guess1:/i)).toBeInTheDocument();
            expect(screen.getByText(/10/i)).toBeInTheDocument();
            expect(screen.getByText(/guess2:/i)).toBeInTheDocument();
            expect(screen.getByText(/20/i)).toBeInTheDocument();
        });
    });

    test('renders no scores available message when fetch returns empty scores', async () => {
        // Mock fetch response with empty scores
        fetch.mockResolvedValueOnce({
            ok: true,
        });

        render(<FriendScoreboard />);

        // Wait for the no scores message to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument();
        });
    });

    test('renders no scores available message when response is not ok', async () => {
        // Mock fetch response with empty scores
        fetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({
                scores: {},
            }),
        });

        render(<FriendScoreboard />);

        // Wait for the no scores message to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument();
        });
    });

    test('handles fetch error gracefully', async () => {
        // Mock fetch to simulate an error
        fetch.mockRejectedValueOnce(new Error('Network error'));

        render(<FriendScoreboard />);

        // Wait for the error handling (if any) to be displayed
        await waitFor(() => {
            expect(screen.getByText(/no scores available/i)).toBeInTheDocument(); // Assuming it falls back to this message
        });
    });
});

describe('ArticleDisplay Component', () => {
    afterEach(() => {
        jest.clearAllMocks(); // Clear mocks after each test
    });

    test('renders only text', async () => {
        // Mock fetch response with only main text and headers
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                article: {
                    "main-text" : "This is a sample article text.",
                    "header" : "Header One",
                    "header-text": "Header text."
                },
            }),
        })

        render(<ArticleDisplay />);

        // Wait for article to render
        await waitFor(() => {
            expect(screen.getByText(/This is a sample article text./i)).toBeInTheDocument();
            expect(screen.getByText(/header one/i)).toBeInTheDocument();
            expect(screen.getByText(/header text./i)).toBeInTheDocument();
            expect(screen.queryByRole('img')).toBeNull(); // Ensure no images are rendered
        });
    });

    test('renders text with image', async () => {
        // Mock fetch response with only main text and image url
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                article: {
                    "main-text" : "This is a sample article text.",
                    "image-url" : "https://i.imgur.com/FAJDCm7.jpeg"
                },
            }),
        })

        render(<ArticleDisplay />);

        // Wait for article to render
        await waitFor(() => {
            expect(screen.getByText(/This is a sample article text./i)).toBeInTheDocument();
            const img = screen.getByRole('img');
            expect(img).toBeInTheDocument();
            expect(img).toHaveAttribute('src', "https://i.imgur.com/FAJDCm7.jpeg"); // Check if the image source is correct
        });
    });

    test('renders text with image along with title and captions', async () => {
        // Mock fetch response with main text, image, title, and captions
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                article: {
                    "main-text" : "This is a sample article text.",
                    "image-url" : "https://i.imgur.com/FAJDCm7.jpeg",
                    "image-title" : "Image Title",
                    "captions" : {
                        "caption1" : "caption 1 text",
                        "caption2" : "caption 2 text"
                    }
                },
            }),
        })

        render(<ArticleDisplay />);

        // Wait for article to render
        await waitFor(() => {
            expect(screen.getByText(/This is a sample article text./i)).toBeInTheDocument();
            const img = screen.getByRole('img');
            expect(img).toBeInTheDocument();
            expect(img).toHaveAttribute('src', "https://i.imgur.com/FAJDCm7.jpeg"); // Check if the image source is correct
            expect(screen.getByText("Image Title")).toBeInTheDocument(); // Check for image title
            expect(screen.getByText("caption 1 text")).toBeInTheDocument(); // Check for image caption
            expect(screen.getByText("caption 2 text")).toBeInTheDocument(); // Check for image caption
        });
    });

    test('renders lorem ipsum when response is not ok', async () => {
        // Mock fetch response with empty scores
        fetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({
            }),
        });

        render(<ArticleDisplay />);

        // Wait for the no scores message to be displayed
        await waitFor(() => {
            const Lorem = screen.getAllByText(/Lorem ipsum/i);
            expect(Lorem.length).toBeGreaterThan(0);
        });
    });

    test('handles fetch error gracefully', async () => {
        // Mock fetch to simulate an error
        fetch.mockRejectedValueOnce(new Error('Network error'));

        render(<ArticleDisplay />);

        // Wait for the error handling (if any) to be displayed
        await waitFor(() => {
            const Lorem = screen.getAllByText(/Lorem ipsum/i);
            expect(Lorem.length).toBeGreaterThan(0);
        });
    });
});

describe('IndexPage Component', () => {
    afterEach(() => {
        jest.clearAllMocks(); // Clear mocks after each test
    });

    test('renders the submit button and handles click', async () => {
        const inputValue = "Test input";

        // Mock successful fetch response for the POST request
        fetch.mockImplementation(() => {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ success: true, data: "mock data" }), // Mock the json method to return a promise
            })
        });

        render(
            <MemoryRouter>
                <IndexPage />
            </MemoryRouter>
        );

        // Simulate user typing in the input
        const input = screen.getByRole('textbox');
        fireEvent.change(input, { target: { value: inputValue } });

        // Simulate clicking the submit button
        const submitButton = screen.getByText(/Submit/i);
        fireEvent.click(submitButton);

        // Wait for the fetch call to be made
        await waitFor(() => {
            expect(fetch).toHaveBeenCalledWith(expect.stringContaining('process_guess/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ guess: inputValue }),
            });

            // Check if the input is cleared after submission
            expect(input.value).toBe('');
        });
    });

    test('handles fetch error', async () => {
        const inputValue = "Test input";

        // Mock successful fetch response for the POST request
        fetch.mockImplementation(() => {
            return Promise.resolve({
                ok: false,
            })
        });

        render(
            <MemoryRouter>
                <IndexPage />
            </MemoryRouter>
        );

        // Simulate user typing in the input
        const input = screen.getByRole('textbox');
        fireEvent.change(input, { target: { value: inputValue } });

        // Simulate clicking the submit button
        const submitButton = screen.getByText(/Submit/i);
        fireEvent.click(submitButton);

        // Wait for the fetch call to be made
        await waitFor(() => {
            expect(fetch).toHaveBeenCalledWith(expect.stringContaining('process_guess/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ guess: inputValue }),
            });

            // Check if the input is cleared after submission
            expect(input.value).toBe('');
        });
    }); 
});