import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./css/TestChurnDisplay.css";

const TestCoverage = () => {
  const location = useLocation();
  const { githubUrl } = location.state || {};
  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");
  const [reportAvailable, setReportAvailable] = useState(false);
  const [reportUrl, setReportUrl] = useState("");
  const [repoName, setRepoName] = useState("");

  useEffect(() => {
    const fetchTestCoverage = async () => {
      try {
        const response = await fetch(`http://localhost:8004/metrics/test-coverage?repo_url=${githubUrl}`);
        const result = await response.json();

        if (result.download_path) {
          setReportAvailable(true);
          setReportUrl(`http://localhost:8004${result.download_path}`);
          setMessage("Report is ready for download.");
          setStatus("success");

          const segments = githubUrl.split("/");
          setRepoName(segments[segments.length - 1]);

          // Auto download
          const link = document.createElement("a");
          link.href = `http://localhost:8004${result.download_path}`;
          link.download = "test_coverage_report.html";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
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
          <p><strong>Status:</strong> {message}</p>
          {reportAvailable && (
            <>
              <a
                href={reportUrl}
                download
                className="download-report-button"
              >
                Download Report
              </a>
              <iframe
                src="http://localhost:8004/metrics/test-coverage-report"
                title="Test Coverage Report"
                style={{
                  width: "100%",
                  height: "600px",
                  border: "1px solid #ccc",
                  marginTop: "1rem",
                }}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default TestCoverage;
