import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import DefectsHistoryPercentageTrend from "../components/DefectsHistoryPercentageTrend";
import axios from "axios";
import '@testing-library/jest-dom';

jest.mock("axios");
jest.mock("react-chartjs-2", () => ({
  Line: ({ data }) => <div data-testid="mock-line-chart">{JSON.stringify(data)}</div>,
}));

describe("DefectsHistoryPercentageTrend Component", () => {
  const mockGithubUrl = "https://github.com/example/repo";

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders no repository selected message when no URL is provided", () => {
    render(<DefectsHistoryPercentageTrend githubUrl={null} />);

    expect(screen.getByText(/no repository selected/i)).toBeInTheDocument();
  });

  test("renders no historical data message when no data is available", async () => {
    axios.get.mockResolvedValueOnce({ data: [] });
    axios.get.mockResolvedValueOnce({ data: [] });

    render(<DefectsHistoryPercentageTrend githubUrl={mockGithubUrl} />);

    await waitFor(() =>
      expect(screen.getByText(/no historical data available/i)).toBeInTheDocument()
    );
  });

  test("renders the chart with provided data", async () => {
    axios.get.mockResolvedValueOnce({
      data: [
        { repo_url: "repo", timestamp: "2023-01-01T00:00:00Z", percentage_bugs_closed: 50 },
      ],
    });

    axios.get.mockResolvedValueOnce({
      data: [
        {
          repoUrl: mockGithubUrl,
          metric: "defects-removed",
          history: [{ time: "2023-01-01T00:00:00Z", value: 60 }],
        },
      ],
    });

    render(<DefectsHistoryPercentageTrend githubUrl={mockGithubUrl} />);

    await waitFor(() => {
      expect(screen.getByTestId("mock-line-chart")).toBeInTheDocument();
    });

    const chartData = screen.getByTestId("mock-line-chart").textContent;
    expect(chartData).toContain("50");
    expect(chartData).toContain("60");
  });
});
