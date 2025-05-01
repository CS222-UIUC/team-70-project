import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { ProfilePage } from '../Components/ProfilePage/ProfilePage';

// Mock axios or fetch if you're using them
global.fetch = jest.fn();

describe('ProfilePage Component', () => {
    const mockProfileData = {
        username: 'testuser',
        email: 'test@example.com',
        total_games_played: 10,
        total_wins: 7,
        win_rate: 70.0,
        current_streak: 3,
        max_streak: 5,
        average_score: 85.5,
        best_score: 95,
        last_played: '2024-03-20',
        is_authenticated: true
    };

    beforeEach(() => {
        fetch.mockReset();
    });

    test('renders loading state initially', () => {
        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );
        expect(screen.getByText(/Loading Profile.../i)).toBeInTheDocument();
    });

    test('renders profile data when fetch is successful', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockProfileData
        });

        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );

        // Wait for the profile data to load
        await waitFor(() => {
            // User details
            expect(screen.getByText('testuser')).toBeInTheDocument();
            expect(screen.getByText('test@example.com')).toBeInTheDocument();

            // Game statistics
            expect(screen.getByText('10')).toBeInTheDocument(); // total_games_played
            expect(screen.getByText('7')).toBeInTheDocument(); // total_wins
            expect(screen.getByText('70%')).toBeInTheDocument(); // win_rate
            expect(screen.getByText('95')).toBeInTheDocument(); // best_score
            expect(screen.getByText('3')).toBeInTheDocument(); // current_streak
            expect(screen.getByText('5')).toBeInTheDocument(); // max_streak
            expect(screen.getByText('85.5')).toBeInTheDocument(); // average_score
            expect(screen.getByText('3/20/2024')).toBeInTheDocument(); // formatted last_played date
        });
    });

    test('renders error message when fetch fails', async () => {
        fetch.mockRejectedValueOnce(new Error('Failed to fetch'));

        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/Error/i)).toBeInTheDocument();
        });
    });

    test('renders "Never" for last played when date is null', async () => {
        const mockDataWithNullDate = {
            ...mockProfileData,
            last_played: null
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockDataWithNullDate
        });

        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('Never')).toBeInTheDocument();
        });
    });

    test('handles unauthorized access', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ error: 'Unauthorized' })
        });

        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/Error/i)).toBeInTheDocument();
            expect(screen.getByText(/Unauthorized/i)).toBeInTheDocument();
        });
    });

    test('verifies all statistic labels are present', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockProfileData
        });

        render(
            <MemoryRouter>
                <ProfilePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            // Check for all statistic labels
            expect(screen.getByText('Games Played')).toBeInTheDocument();
            expect(screen.getByText('Games Won')).toBeInTheDocument();
            expect(screen.getByText('Win Rate')).toBeInTheDocument();
            expect(screen.getByText('Best Score')).toBeInTheDocument();
            expect(screen.getByText('Current Streak')).toBeInTheDocument();
            expect(screen.getByText('Max Streak')).toBeInTheDocument();
            expect(screen.getByText('Average Score')).toBeInTheDocument();
            expect(screen.getByText('Last Played')).toBeInTheDocument();
        });
    });
});