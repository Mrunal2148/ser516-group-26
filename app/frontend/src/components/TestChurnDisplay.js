import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import "./css/TestChurnDisplay.css";

const TestChurnDisplay = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const location = useLocation();
  const { owner, repo } = location.state || {};
  const [reportAvailable, setReportAvailable] = useState(false);
  const [reportUrl, setReportUrl] = useState("");

  const fetchTestChurn = async () => {
    if (!startDate || !endDate) {
      alert("Please select both start and end dates.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8080/api/test-churn/calculate?owner=${owner}&repo=${repo}&startDate=${startDate}&endDate=${endDate}`
      );
      const result = await response.json();
      setData(result);

      // Check if the report is available
      if (result.report_download_url && result.report_download_url !== "Report not found") {
        setReportAvailable(true);
        setReportUrl(`http://localhost:8080${result.report_download_url}`);
      } else {
        setReportAvailable(false);
      }
    } catch (error) {
      console.error("Error fetching test churn data:", error);
    }
    setLoading(false);
  };

  return (
    <div className="test-churn-container">
      <h2 className="test-churn-title">Test Churn for: {repo}</h2>
      <div className="input-group">
        <label>Start Date:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="date-input"
        />
        <label>End Date:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="date-input"
        />
      </div>
      <button
        onClick={fetchTestChurn}
        disabled={loading}
        className="fetch-button"
      >
        {loading ? "Loading..." : "Fetch Test Churn Data"}
      </button>
      {data && (
        <div className="test-churn-report">
          <h2 className="report-title">Test Churn Report</h2>
          <div className="report-details">
            <p><strong>Modified Tests:</strong> {data.modified_tests}</p>
            <p><strong>Added Tests:</strong> {data.added_tests}</p>
            <p><strong>Deleted Tests:</strong> {data.deleted_tests}</p>
            <p><strong>Timestamp:</strong> {data.timestamp}</p>
          </div>
          {reportAvailable && (
            <a
              href={reportUrl}
              download
              className="download-report-button"
            >
              Download Report
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default TestChurnDisplay;
