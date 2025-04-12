import React from "react";
import { render, screen } from "@testing-library/react";
import DefectMetricsChart from "../components/DefectMetricsChart";
import '@testing-library/jest-dom';

jest.mock("react-chartjs-2", () => ({
  Bar: ({ data }) => <div data-testid="mock-bar-chart">{JSON.stringify(data)}</div>,
}));

describe("DefectMetricsChart Component", () => {
  test("renders no data message when no data is provided", () => {
    render(<DefectMetricsChart data={null} />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  test("renders the chart with provided data", () => {
    const mockData = {
      weeklyClosedBugs: { "2023-W01": 4, "2023-W02": 5 },
      weeklyOpenedBugs: { "2023-W01": 6, "2023-W02": 7 },
    };

    render(<DefectMetricsChart data={mockData} />);

    expect(screen.getByTestId("mock-bar-chart")).toBeInTheDocument();
  });
});
