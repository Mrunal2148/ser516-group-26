import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import CoverageDashboard from "../components/CoverageDashboard";
import axios from "axios";
jest.mock("axios");

const mockGithubUrl = "https://github.com/example/repo";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useLocation: () => ({ state: { githubUrl: mockGithubUrl } }),
}));

describe("CoverageDashboard Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders coverage breakdown and benchmark chart if data exists", async () => {
    axios.get.mockResolvedValueOnce({
      data: [
        {
          repo_url: mockGithubUrl,
          total_lines: 100,
          comment_lines: 42,
          coverage: 42,
          timestamp: "2024-04-01",
        },
        {
          repo_url: mockGithubUrl,
          total_lines: 90,
          comment_lines: 36,
          coverage: 40,
          timestamp: "2024-03-25",
        },
      ],
    });

    await act(async () => {
      render(<CoverageDashboard selectedRepo={mockGithubUrl} benchmarks={[]} />);
    });

    await waitFor(() => {
      expect(screen.getByText("Coverage Breakdown")).toBeInTheDocument();
    });
  });

  test("shows error message if axios call fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("Failed to fetch coverage"));

    await act(async () => {
      render(<CoverageDashboard selectedRepo={mockGithubUrl} benchmarks={[]} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/error fetching coverage data/i)).toBeInTheDocument();
    });
  });

  test("renders no history message if filtered data is empty", async () => {
    axios.get.mockResolvedValueOnce({ data: [] });

    await act(async () => {
      render(<CoverageDashboard selectedRepo={mockGithubUrl} benchmarks={[]} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/no coverage data available/i)).toBeInTheDocument();
    });
  });
});
