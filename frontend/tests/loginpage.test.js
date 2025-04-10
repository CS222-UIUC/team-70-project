import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import Login from '../src/Components/Login/Login';
import Signup from '../src/Components/Signup/Signup';
import { ProfilePage } from '../src/Components/ProfilePage/ProfilePage';

// Mock axios
jest.mock('axios');

// Mock React Router's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Helper function to wrap components with Router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock CSRF token fetch based on your actual implementation
    axios.get.mockResolvedValueOnce({ 
      data: { csrfToken: 'fake-csrf-token' }
    });
  });

  test('renders login form', () => {
    renderWithRouter(<Login />);
    expect(screen.getByLabelText(/username:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password:/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });


});



describe('Profile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock CSRF token fetch
    axios.get.mockResolvedValueOnce({ 
      data: { csrfToken: 'fake-csrf-token' }
    });
  });

  

  

  test('handles profile fetch error', async () => {
    // Mock error response after CSRF token fetch
    axios.get.mockImplementation((url) => {
      if (url === 'http://localhost:8000/csrf/') {
        return Promise.resolve({ data: { csrfToken: 'fake-csrf-token' } });
      }
      return Promise.reject({ response: { status: 500 } });
    });
    
    renderWithRouter(<ProfilePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load profile data/i)).toBeInTheDocument();
    });
  });
});