import React from "react";
import { render, screen, waitFor, fireEvent, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import axios from "axios";
import CodeComment from "../components/CodeComment";
import '@testing-library/jest-dom';

jest.mock("axios");
jest.mock("../components/CoverageDashboard", () => () => <div>Mocked CoverageDashboard</div>);

describe("CodeComment Component", () => {
  const mockGithubUrl = "https://github.com/example/repo";
  const mockMetric = "code-comment-coverage";

  const mockLocationState = {
    state: { githubUrl: mockGithubUrl, metric: mockMetric },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    axios.post.mockResolvedValue({ data: { coverage: 42.42 } });
    axios.get.mockResolvedValue({ data: [] });
  });

  test("renders the component with repository link", async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    expect(screen.getByText("Code Comment Coverage")).toBeInTheDocument();
    expect(screen.getByText("Repository:")).toBeInTheDocument();
    expect(screen.getByText(mockGithubUrl)).toBeInTheDocument();
  });

  test("displays error message when coverage analysis fails", async () => {
    axios.post.mockRejectedValueOnce(new Error("Failed to analyze repository"));

    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    await waitFor(() =>
      expect(
        screen.getByText(/failed to analyze repository coverage/i)
      ).toBeInTheDocument()
    );
  });

  test("displays coverage data when analysis succeeds", async () => {
    axios.post.mockResolvedValueOnce({ data: { coverage: 42.42} });
    axios.get.mockResolvedValueOnce({ data: [] });
    axios.get.mockResolvedValueOnce({ data: [] });

    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    await waitFor(() =>
      expect(screen.getByText("Comment Coverage")).toBeInTheDocument()
    );

    expect(screen.getByText("42.42%"))?.toBeInTheDocument();
    expect(screen.getByText(mockGithubUrl)).toBeInTheDocument();
    expect(
      screen.queryByText(/failed to analyze repository coverage/i)
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/failed to fetch benchmarks/i)
    ).not.toBeInTheDocument();
  });

  test("displays error message when fetching benchmarks fails", async () => {
    axios.post.mockResolvedValueOnce({ data: { coverage: 42.42} });
    axios.get.mockResolvedValueOnce({ data: [] });
    axios.get.mockRejectedValueOnce(new Error("Failed to fetch benchmarks"));

    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    await waitFor(() =>
      expect(
        screen.getByText(/failed to fetch benchmarks/i)
      ).toBeInTheDocument()
    );
  });

  test("displays loading message while analyzing coverage", async () => {
    axios.post.mockImplementationOnce(() => new Promise(() => {})); // Simulate a pending request
    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    expect(screen.getByText(/analyzing coverage/i)).toBeInTheDocument();
  });

  test("opens and closes the benchmark modal", async () => {
    axios.post.mockResolvedValueOnce({ data: { coverage: 42.42} });
    axios.get.mockResolvedValueOnce({ data: [] });
    axios.get.mockResolvedValueOnce({ data: [] });

    await act(async () => {
      render(
        <MemoryRouter initialEntries={[mockLocationState]}>
          <CodeComment />
        </MemoryRouter>
      );
    });

    await waitFor(() =>
      expect(screen.getByText("Comment Coverage")).toBeInTheDocument()
    );

    const addBenchmarkButton = screen.getByText("Add Benchmark");
    fireEvent.click(addBenchmarkButton);

    expect(screen.getByText("X")).toBeInTheDocument();

    const closeModalButton = screen.getByText("X");
    fireEvent.click(closeModalButton);

    await waitFor(() =>
      expect(screen.queryByText("X")).not.toBeInTheDocument()
    );
  });
});
