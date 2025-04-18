import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./css/TestChurnDisplay.css";

const TestCoverage = () => {
  const location = useLocation();
  const { githubUrl } = location.state || {};
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  const [reportAvailable, setReportAvailable] = useState(false);
  const [repoName, setRepoName] = useState("");

  useEffect(() => {
    const fetchTestCoverage = async () => {
      try {
        const response = await fetch(
          `http://localhost:8004/metrics/test-coverage?repo_url=${githubUrl}`
        );
        const result = await response.json();

        if (result.download_path) {
          setReportAvailable(true);
          setMessage("Report is ready for download.");
          setStatus("success");

          const segments = githubUrl.split("/");
          setRepoName(segments[segments.length - 1]);
        } else {
          setStatus("error");
          setMessage(result.error || "No report available.");
        }
      } catch (error) {
        setStatus("error");
        setMessage("Failed to fetch test coverage.");
      }
    };

    if (githubUrl) {
      fetchTestCoverage();
    } else {
      setStatus("error");
      setMessage("GitHub URL not provided.");
    }
  }, [githubUrl]);

  return (
    <div className="test-churn-container">
      <h2 className="test-churn-title">Test Coverage for: {repoName}</h2>

      {status === "loading" && <p>Fetching test coverage report...</p>}

      {status === "error" && <p style={{ color: "red" }}>{message}</p>}

      {status === "success" && (
        <div className="test-churn-report">
          <h2 className="report-title">Test Coverage Report</h2>
          <p>
            <strong>Status:</strong> {message}
          </p>

          {reportAvailable && (
            <a
              href="http://localhost:8004/metrics/test-coverage-report/download"
              download="test_coverage_report.pdf"
              className="download-report-button"
              style={{
                display: "inline-block",
                marginTop: "12px",
                padding: "10px 16px",
                backgroundColor: "#4caf50",
                color: "#fff",
                textDecoration: "none",
                borderRadius: "6px",
              }}
            >
              Download Report (PDF)
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default TestCoverage;
