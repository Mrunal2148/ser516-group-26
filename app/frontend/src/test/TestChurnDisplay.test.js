import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import TestChurnDisplay from "../components/TestChurnDisplay";
import '@testing-library/jest-dom';

// Silence React Router v7 warnings during tests
beforeAll(() => {
  jest.spyOn(console, 'warn').mockImplementation((msg) => {
    if (
      msg.includes('React Router will begin wrapping') ||
      msg.includes('Relative route resolution within Splat routes')
    ) return;
    console.warn(msg);
  });
});

beforeEach(() => {
  fetch.resetMocks();
});

const renderWithRouter = (ui, { route = "/", state = {} } = {}) => {
  return render(
    <MemoryRouter initialEntries={[{ pathname: route, state }]}>
      <Routes>
        <Route path="/" element={ui} />
      </Routes>
    </MemoryRouter>
  );
};

describe("TestChurnDisplay Component", () => {
  const mockOwner = "example-owner";
  const mockRepo = "example-repo";

  test("renders correctly with inputs and fetch button", () => {
    renderWithRouter(<TestChurnDisplay />, {
      state: { owner: mockOwner, repo: mockRepo },
    });

    expect(screen.getByText(`Test Churn for: ${mockRepo}`)).toBeInTheDocument();
    expect(screen.getByLabelText(/Start Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/End Date/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /fetch test churn data/i })).toBeInTheDocument();
  });

  test("shows alert when start or end date is missing", () => {
    window.alert = jest.fn(); // mock alert
    renderWithRouter(<TestChurnDisplay />, {
      state: { owner: mockOwner, repo: mockRepo },
    });

    fireEvent.click(screen.getByRole("button", { name: /fetch test churn data/i }));
    expect(window.alert).toHaveBeenCalledWith("Please select both start and end dates.");
  });

//   test("fetches and displays test churn data successfully", async () => {
//     const mockData = {
//       added_tests: 5,
//       deleted_tests: 3,
//       modified_tests: 2,
//       timestamp: "2024-04-11T10:00:00Z",
//       report_download_url: "/api/test-churn/report/test_churn_report.md",
//     };

//     fetch.mockResponseOnce(JSON.stringify(mockData));

//     renderWithRouter(<TestChurnDisplay />, {
//       state: { owner: mockOwner, repo: mockRepo },
//     });

//     fireEvent.change(screen.getByLabelText(/Start Date/i), {
//       target: { value: "2024-04-01" },
//     });
//     fireEvent.change(screen.getByLabelText(/End Date/i), {
//       target: { value: "2024-04-10" },
//     });

//     fireEvent.click(screen.getByRole("button", { name: /fetch test churn data/i }));

//     await waitFor(() => {
//       expect(
//         screen.getByText((content, element) =>
//           element.tagName.toLowerCase() === 'p' &&
//           content.includes("Modified Tests:") &&
//           content.includes("2")
//         )
//       ).toBeInTheDocument();

//       expect(
//         screen.getByText((content, element) =>
//           element.tagName.toLowerCase() === 'p' &&
//           content.includes("Added Tests:") &&
//           content.includes("5")
//         )
//       ).toBeInTheDocument();

//       expect(
//         screen.getByText((content, element) =>
//           element.tagName.toLowerCase() === 'p' &&
//           content.includes("Deleted Tests:") &&
//           content.includes("3")
//         )
//       ).toBeInTheDocument();

//       expect(
//         screen.getByText((content, element) =>
//           element.tagName.toLowerCase() === 'p' &&
//           content.includes("Timestamp:") &&
//           content.includes(mockData.timestamp)
//         )
//       ).toBeInTheDocument();
//     });

//     expect(screen.getByRole("link", { name: /Download Report/i })).toHaveAttribute(
//       "href",
//       `http://localhost:8080${mockData.report_download_url}`
//     );
//   });

  test("does not show download link when report is unavailable", async () => {
    const mockData = {
      added_tests: 1,
      deleted_tests: 0,
      modified_tests: 0,
      timestamp: "2024-04-11T10:00:00Z",
      report_download_url: "Report not found",
    };

    fetch.mockResponseOnce(JSON.stringify(mockData));

    renderWithRouter(<TestChurnDisplay />, {
      state: { owner: mockOwner, repo: mockRepo },
    });

    fireEvent.change(screen.getByLabelText(/Start Date/i), {
      target: { value: "2024-04-01" },
    });
    fireEvent.change(screen.getByLabelText(/End Date/i), {
      target: { value: "2024-04-10" },
    });

    fireEvent.click(screen.getByRole("button", { name: /fetch test churn data/i }));

    await waitFor(() => {
      expect(screen.getByText("Test Churn Report")).toBeInTheDocument();
    });

    expect(screen.queryByRole("link", { name: /Download Report/i })).not.toBeInTheDocument();
  });

  test("handles fetch failure gracefully", async () => {
    fetch.mockRejectOnce(() => Promise.reject("API is down"));

    renderWithRouter(<TestChurnDisplay />, {
      state: { owner: mockOwner, repo: mockRepo },
    });

    fireEvent.change(screen.getByLabelText(/Start Date/i), {
      target: { value: "2024-04-01" },
    });
    fireEvent.change(screen.getByLabelText(/End Date/i), {
      target: { value: "2024-04-10" },
    });

    fireEvent.click(screen.getByRole("button", { name: /fetch test churn data/i }));

    await waitFor(() =>
      expect(screen.queryByText("Test Churn Report")).not.toBeInTheDocument()
    );
  });
});
