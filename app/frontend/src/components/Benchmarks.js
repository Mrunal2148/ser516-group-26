import React, { useState, useEffect } from "react";
import Tooltip from "@mui/material/Tooltip";
import "./css/RunMetrics.css";

const Benchmarks = ({ githubUrl, selectedMetric: initialMetric }) => {
  const [selectedMetric, setSelectedMetric] = useState(initialMetric || "code-comment-coverage");
  const [benchmarkValue, setBenchmarkValue] = useState(""); 
  const [showTooltip, setShowTooltip] = useState(false); 

  useEffect(() => {
    console.log("Received githubUrl:", githubUrl);
    console.log("Received metric:", initialMetric);
  }, [githubUrl, initialMetric]);

  const handleSaveBenchmark = () => {
    const benchmarkData = {
      repoUrl: githubUrl,
      metric: selectedMetric,
      history: [
        {
          value: parseFloat(benchmarkValue),
          time: new Date().toISOString(),
        },
      ],
    };

    console.log("Sending benchmark data:", benchmarkData);

    if (!benchmarkData.repoUrl || !benchmarkData.metric || isNaN(benchmarkData.history[0].value)) {
      console.error("Invalid data:", benchmarkData);
      alert("Error: Missing required fields or invalid benchmark value.");
      return;
    }

    fetch("http://127.0.0.1:5005/save-benchmark", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(benchmarkData),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            console.error("Server error:", err);
            throw new Error(`Network response was not ok: ${response.statusText}`);
          });
        }
        return response.json();
      })
      .then(() => {
        alert("Benchmark saved successfully!");
      })
      .catch((error) => {
        console.error("Error saving benchmark:", error);
      });
  };

  const handleBenchmarkValueChange = (e) => {
    const value = e.target.value;
    if (/^\d*\.?\d*$/.test(value)) {
      setBenchmarkValue(value);
      setShowTooltip(false);
    } else {
      setShowTooltip(true);
    }
  };

  return (
    <div>
      <h1>Your Own Benchmarks!</h1>
      <div className="run-metrics-container">
        <p><strong>Repository:</strong> {githubUrl}</p>
        <p><strong>Metric:</strong> {selectedMetric}</p>

        <div className="benchmark-input">
          <label>Benchmark Value: &nbsp; </label>
          <Tooltip title="Only numbers are allowed" open={showTooltip} arrow>
            <input
              type="text"
              value={benchmarkValue}
              onChange={handleBenchmarkValueChange}
            />
          </Tooltip>
        </div>
        <br />

        <button
          className="run-button"
          onClick={handleSaveBenchmark}
          disabled={!benchmarkValue}
        >
          Save Benchmark
        </button>
      </div>
    </div>
  );
};

export default Benchmarks;