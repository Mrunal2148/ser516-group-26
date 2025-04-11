import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import FogIndexCalculator from '../components/FogIndexCalculator';
import { useLocation } from 'react-router-dom';

jest.mock('react-router-dom', () => ({
    useLocation: jest.fn(),
}));

beforeEach(() => {
    // Default to no githubUrl
    useLocation.mockReturnValue({ state: { githubUrl: null } });
});

test('renders Fog Index Calculator header', () => {
    render(<FogIndexCalculator />);
    expect(screen.getByText('Fog Index Calculator')).toBeInTheDocument();
});

test('does NOT render repository link when githubUrl is null', () => {
    render(<FogIndexCalculator />);
    // queryByRole returns null if not found
    expect(screen.queryByRole('link')).toBeNull();
});

test('renders repository link when githubUrl is provided', () => {
    // Override for this case
    useLocation.mockReturnValue({
        state: { githubUrl: 'https://github.com/test/repo' }
    });

    render(<FogIndexCalculator />);

    // Should find a link with that URL
    const link = screen.getByRole('link', {
        name: /https:\/\/github\.com\/test\/repo/i
    });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://github.com/test/repo');
});
