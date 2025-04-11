import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import FogIndexChart from '../components/FogIndexChart';

// Mock out the Bar chart so it just renders a div
jest.mock('react-chartjs-2', () => ({
    Bar: () => <div data-testid="bar-chart" />,
}));

test('renders fallback text when no data prop is passed', () => {
    render(<FogIndexChart data={null} />);

    // Should show the "No data available" paragraph
    expect(screen.getByText(/No data available/i)).toBeInTheDocument();
});

test('renders Bar chart when data prop is provided', () => {
    const sample = { fogIndex: 5, averageSentenceLength: 10, percentageComplexWords: 20 };
    render(<FogIndexChart data={sample} />);

    // Should mount our mocked Bar chart
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
});
