import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SelectDropdown from "./Dropdown";
import "./css/RunMetrics.css";

const RunMetrics = () => {
  const [links, setLinks] = useState([]);
  const [selectedLink, setSelectedLink] = useState("");
  const [selectedMetrics, setSelectedMetrics] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:5005/links.json")
      .then((response) => response.json())
      .then((data) => setLinks(data))
      .catch((error) => console.error("Error fetching links:", error));
  }, []);

  const handleMetricChange = (metric) => {
    setSelectedMetrics((prevMetrics) =>
      prevMetrics.includes(metric)
        ? prevMetrics.filter((m) => m !== metric) // Remove if already selected
        : [...prevMetrics, metric] // Add new metric
    );
  };

  const handleRun = () => {
    if (!selectedLink || selectedMetrics.length === 0) return;

    const owner = selectedLink.split("/").slice(-2, -1)[0];
    const repo = selectedLink.split("/").pop();

    // If multiple metrics are selected, navigate to MultiMetrics page
    if (selectedMetrics.length > 1) {
      navigate("/multi-metrics", { state: { selectedMetrics, githubUrl: selectedLink, owner, repo } });
    } else {
      //  If only one metric is selected, navigate to its specific page
      switch (selectedMetrics[0]) {
        case "fog-index":
          navigate("/fogindex", { state: { githubUrl: selectedLink } });
          break;
        case "code-comment-coverage":
          navigate("/codecomment", { state: { githubUrl: selectedLink } });
          break;
        case "defects-removed":
          navigate("/defectsremoved", { state: { owner, repo } });
          break;
        case "test-churn":
          navigate("/testChurn", { state: { owner, repo } });
          break;
        default:
          alert("Invalid metric");
          break;
      }
    }
  };

  return (
    <div className="run-metrics-container">
      <h2>Run Metrics Dashboard</h2>

      <SelectDropdown
        label="Select Repository"
        options={links.slice(1).map((link) => ({ label: link, value: link }))}
        selectedValue={selectedLink}
        onSelect={setSelectedLink}
      />

      {/* Multiple Checkbox Selection for Metrics */}
      <div className="multi-select">
        <label>Select Metrics:</label>
        <div className="checkbox">
          <input
            type="checkbox"
            id="fog-index"
            checked={selectedMetrics.includes("fog-index")}
            onChange={() => handleMetricChange("fog-index")}
          />
          <label htmlFor="fog-index">Fog Index</label>
        </div>

        <div className="checkbox">
          <input
            type="checkbox"
            id="code-comment-coverage"
            checked={selectedMetrics.includes("code-comment-coverage")}
            onChange={() => handleMetricChange("code-comment-coverage")}
          />
          <label htmlFor="code-comment-coverage">Code Comment Coverage</label>
        </div>

        <div className="checkbox">
          <input
            type="checkbox"
            id="defects-removed"
            checked={selectedMetrics.includes("defects-removed")}
            onChange={() => handleMetricChange("defects-removed")}
          />
          <label htmlFor="defects-removed">Defects Removed</label>
        </div>
        <div className="checkbox">
          <input
            type="checkbox"
            id="test-churn"
            checked={selectedMetrics.includes("test-churn")}
            onChange={() => handleMetricChange("test-churn")}
          />
          <label htmlFor="test-churn">Test Churn</label>
        </div>
      </div>

      <button 
        className="run-button" 
        onClick={handleRun} 
        disabled={!selectedLink || selectedMetrics.length === 0}
      >
        Run
      </button>
    </div>
  );
};

export default RunMetrics;
