import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import FogIndexCalculator from '../components/FogIndexCalculator';

// ✅ Global fetch mock
global.fetch = vi.fn();

// ✅ Mock all subcomponents properly (return object with default)
vi.mock('../components/FogIndexChart', () => ({
    default: () => React.createElement('div', null, 'Mocked FogIndexChart'),
}));

vi.mock('../components/FogIndexBenchmarked', () => ({
    default: () => React.createElement('div', null, 'Mocked BenchmarkedChart'),
}));

vi.mock('../components/Benchmarks', () => ({
    default: () => React.createElement('div', null, 'Mocked Benchmarks'),
}));

// ✅ Mock useLocation
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useLocation: () => ({
            state: {
                githubUrl: 'https://github.com/your/repo',
            },
        }),
    };
});

describe('FogIndexCalculator', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    test('renders and displays fetched Fog Index', async () => {
        const mockResponse = { fogIndex: 12.5 };

        fetch
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([
                    { generatedTime: '2025-04-01T10:00:00Z', fogIndex: 15 },
                ]),
            })
            .mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve([
                    {
                        repoUrl: 'https://github.com/your/repo',
                        metric: 'fog-index',
                        history: [{ time: '2025-04-01T10:00:00Z', value: 10 }],
                    },
                ]),
            });

        render(React.createElement(FogIndexCalculator));

        // ✅ Match cell with the Fog Index value
        await waitFor(() => {
            const valueCell = screen.getByRole('cell', { name: '12.5' });
            expect(valueCell).toBeInTheDocument();
        });

        expect(fetch).toHaveBeenCalledTimes(3);
    });
});
