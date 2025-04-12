import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FogIndexBenchmarked from '../components/FogIndexBenchmarked';

// Mock out the Line chart so it just renders a div
jest.mock('react-chartjs-2', () => ({
    Line: () => <div data-testid="line-chart" />,
}));

beforeEach(() => {
    global.fetch = jest.fn((url) => {
        if (url.includes('/api/fog-index/history')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve([]), // empty historyData
            });
        }
        if (url.includes('/benchmarks.json')) {
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve([]), // empty benchmarkHistory
            });
        }
        return Promise.reject(new Error('Unexpected URL: ' + url));
    });
});

test('shows no-benchmark message when there is no benchmark data', async () => {
    render(<FogIndexBenchmarked repoUrl="https://github.com/user/repo" />);

    // wait for the effect to run
    await waitFor(() => {
        expect(
            screen.getByText(/No benchmark data available/i)
        ).toBeInTheDocument();
    });

    // and our mocked chart still mounts
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
});
