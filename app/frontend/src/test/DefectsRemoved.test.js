import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import DefectsRemoved from "../pages/DefectsRemoved";
import '@testing-library/jest-dom';

global.fetch = jest.fn();

jest.mock("../components/DefectMetricsChart", () => () => <div data-testid="mock-defect-metrics-chart" />);
jest.mock("../components/DefectsHistoryPercentageTrend", () => () => <div data-testid="mock-defects-history-trend" />);
jest.mock("../components/Benchmarks", () => () => <div data-testid="mock-benchmarks" />);

describe("DefectsRemoved Component", () => {
  const mockOwner = "example-owner";
  const mockRepo = "example-repo";

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders error message when no repository is selected", () => {
    render(
      <MemoryRouter>
        <DefectsRemoved />
      </MemoryRouter>
    );

    expect(screen.getByText(/no repository selected/i)).toBeInTheDocument();
  });

  test("renders loading message while fetching data", async () => {
    fetch.mockImplementationOnce(() => new Promise(() => {}));

    render(
      <MemoryRouter initialEntries={[{ state: { owner: mockOwner, repo: mockRepo } }]}>
        <DefectsRemoved />
      </MemoryRouter>
    );

    expect(screen.getByText(/loading bug statistics/i)).toBeInTheDocument();
  });

  test("renders error message when fetch fails", async () => {
    fetch.mockRejectedValueOnce(new Error("Failed to fetch data"));

    render(
      <MemoryRouter initialEntries={[{ state: { owner: mockOwner, repo: mockRepo } }]}>
        <DefectsRemoved />
      </MemoryRouter>
    );

    await waitFor(() =>
      expect(screen.getByText("Failed to fetch data")).toBeInTheDocument()
    );
  });

  test("renders defect data when fetch succeeds", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        totalOpenedBugs: 10,
        totalClosedBugs: 8,
        startWeek: "2023-W01",
        endWeek: "2023-W52",
        weeklyOpenedBugs: { "2023-W01": 5, "2023-W02": 5 },
        weeklyClosedBugs: { "2023-W01": 4, "2023-W02": 4 },
      }),
    });

    render(
      <MemoryRouter initialEntries={[{ state: { owner: mockOwner, repo: mockRepo } }]}>
        <DefectsRemoved />
      </MemoryRouter>
    );

    await waitFor(() => {
      screen.debug();

      expect(screen.getByText("Total Opened Bugs")).toBeInTheDocument();
      expect(screen.getByText("Total Closed Bugs")).toBeInTheDocument();
      expect(screen.getByText("Start Week")).toBeInTheDocument();
      expect(screen.getByText("End Week")).toBeInTheDocument();

      const tableRows = screen.getAllByRole("row");
      expect(tableRows).toHaveLength(2); // Header row + data row

      const dataRow = tableRows[1];
      expect(dataRow).toHaveTextContent("10");
      expect(dataRow).toHaveTextContent("8");
      expect(dataRow).toHaveTextContent("2023-W01");
      expect(dataRow).toHaveTextContent("2023-W02");
    });

    expect(screen.getByTestId("mock-defect-metrics-chart")).toBeInTheDocument();
    expect(screen.getByTestId("mock-defects-history-trend")).toBeInTheDocument();
  });

  test("opens and closes the benchmark modal", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        totalOpenedBugs: 10,
        totalClosedBugs: 8,
        startWeek: "2023-W01",
        endWeek: "2023-W52",
        weeklyOpenedBugs: { "2023-W01": 5, "2023-W02": 5 },
        weeklyClosedBugs: { "2023-W01": 4, "2023-W02": 4 },
      }),
    });

    render(
      <MemoryRouter initialEntries={[{ state: { owner: mockOwner, repo: mockRepo } }]}>
        <DefectsRemoved />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Total Opened Bugs")).toBeInTheDocument();
    });

    const addBenchmarkButton = screen.getByText("Add Benchmark");
    fireEvent.click(addBenchmarkButton);

    expect(screen.getByTestId("mock-benchmarks")).toBeInTheDocument();

    const closeModalButton = screen.getByText("X");
    fireEvent.click(closeModalButton);

    await waitFor(() =>
      expect(screen.queryByTestId("mock-benchmarks")).not.toBeInTheDocument()
    );
  });
});
