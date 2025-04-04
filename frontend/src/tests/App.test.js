import React from 'react';
import { render, screen } from '@testing-library/react';
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

// 