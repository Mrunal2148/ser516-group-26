import React from "react";
import { render, screen } from "@testing-library/react";
import CombinedCoverageChart from "../components/CombinedCoverageChart";
import '@testing-library/jest-dom';

jest.mock("react-chartjs-2", () => ({
  Line: ({ data }) => <div data-testid="mock-line-chart">{JSON.stringify(data)}</div>,
}));

describe("CombinedCoverageChart Component", () => {
  const mockData = [
    { timestamp: "2024-04-01T00:00:00Z", coverage: 0.42 },
    { timestamp: "2024-03-25T00:00:00Z", coverage: 0.4 },
  ];

  const mockBenchmarks = [
    {
      repoUrl: "https://github.com/example/repo",
      metric: "code-comment-coverage",
      history: [
        { time: "2024-03-20T00:00:00Z", value: 35 },
        { time: "2024-03-30T00:00:00Z", value: 40 },
      ],
    },
  ];

  const mockGithubUrl = "https://github.com/example/repo";

  test("renders the chart with provided data and benchmarks", () => {
    render(
      <CombinedCoverageChart
        data={mockData}
        githubUrl={mockGithubUrl}
        benchmarks={mockBenchmarks}
      />
    );

    expect(screen.getByTestId("mock-line-chart")).toBeInTheDocument();

    const chartData = JSON.parse(screen.getByTestId("mock-line-chart").textContent);
    expect(chartData.labels).toEqual([
      "4/1/2024, 12:00:00 AM",
      "3/25/2024, 12:00:00 AM",
    ]);
    expect(chartData.datasets).toHaveLength(2);
    expect(chartData.datasets[0].label).toBe("Benchmark Coverage");
    expect(chartData.datasets[1].label).toBe("Code Comment Coverage (%) Over Time");
  });

  test("renders a message when no benchmark data is available", () => {
    render(
      <CombinedCoverageChart
        data={mockData}
        githubUrl={mockGithubUrl}
        benchmarks={[]}
      />
    );

    expect(
      screen.getByText(/no benchmark data available/i)
    ).toBeInTheDocument();
  });

});
