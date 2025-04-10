import React from "react";
import { render, screen } from "@testing-library/react";
import CoverageChart from "../components/CoverageChart";
import '@testing-library/jest-dom';
import axios from "axios";
 
jest.mock("axios");

// Mock recharts to avoid rendering actual charts
jest.mock("recharts", () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="mock-responsive-container">{children}</div>,
  BarChart: ({ children }) => <div data-testid="mock-bar-chart">{children}</div>,
  XAxis: () => <div data-testid="mock-x-axis" />,
  YAxis: () => <div data-testid="mock-y-axis" />,
  Tooltip: () => <div data-testid="mock-tooltip" />,
  Legend: () => <div data-testid="mock-legend" />,
  Bar: ({ dataKey }) => <div data-testid={`mock-bar-${dataKey}`} />,
}));

describe("CoverageChart Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    axios.get.mockResolvedValue({ data: [] });
  });
  const mockChartData = [
    { name: "Measurement 1", value: 50 },
    { name: "Measurement 2", value: 75 },
    { name: "Measurement 3", value: 100 },
  ];

  test("renders the chart with provided data", () => {
    render(<CoverageChart chartData={mockChartData} />);

    expect(screen.getByTestId("mock-bar-chart")).toBeInTheDocument();
    expect(screen.getByTestId("mock-bar-value")).toBeInTheDocument();
  });

  test("renders an empty chart when no data is provided", () => {
    render(<CoverageChart chartData={[]} />);

    // Chart should be rendered
    expect(screen.getByTestId("mock-bar-chart")).toBeInTheDocument();

    // Chart should not have any data
    expect(screen.getByTestId("mock-bar-chart")).not.toHaveTextContent("Measurement 1");
    expect(screen.getByTestId("mock-bar-chart")).not.toHaveTextContent("Measurement 2");
    expect(screen.getByTestId("mock-bar-chart")).not.toHaveTextContent("Measurement 3");
  });
});
