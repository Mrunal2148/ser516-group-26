import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../components/css/DefectsRemoved.css";
import DefectMetricsChart from "../components/DefectMetricsChart";
import DefectsHistoryPercentageTrend from "../components/DefectsHistoryPercentageTrend";
import Benchmarks from "../components/Benchmarks";

const DefectsRemoved = () => {
  const location = useLocation();
  const { owner, repo } = location.state || {};

  const [bugStats, setBugStats] = useState(null);
  const [error, setError] = useState(null);
  const [showBenchmarkModal, setShowBenchmarkModal] = useState(false);

  useEffect(() => {
    if (!owner || !repo) {
      setError("No repository selected. Please select a valid repository.");
      return;
    }

    fetch(`http://localhost:8080/api/github/defects-stats?owner=${owner}&repo=${repo}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.status} ${response.statusText}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!data || Object.keys(data).length === 0) {
          setError("No defect data available for this repository.");
          return;
        }

        // 1. Gather all "year-week" keys
        const openedKeys = Object.keys(data.weeklyOpenedBugs || {});
        const closedKeys = Object.keys(data.weeklyClosedBugs || {});
        const allKeys = [...new Set([...openedKeys, ...closedKeys])];

        // 2. Sort them numerically by year, then week
        allKeys.sort((a, b) => {
          const [yearA, wA] = a.split("-W");
          const [yearB, wB] = b.split("-W");
          return parseInt(yearA) - parseInt(yearB) || parseInt(wA) - parseInt(wB);
        });

        // 3. Earliest is startWeek, latest is endWeek
        data.startWeek = allKeys[0] ?? "N/A";
        data.endWeek = allKeys[allKeys.length - 1] ?? "N/A";

        setBugStats(data);
        setError(null);
      })
      .catch((error) => setError(error.message));
  }, [owner, repo]);

  const githubUrl = owner && repo ? `https://github.com/${owner}/${repo}` : "";

  return (
    <div className="defects-container card">
      <h2 className="code-comment-title">Defects Removed Metrics</h2>

      {githubUrl && (
        <p className="defects-repo">
          <b>Repository:</b>{" "}
          <a href={githubUrl} target="_blank" rel="noopener noreferrer">
            {githubUrl}
          </a>
        </p>
      )}

      {error ? (
        <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>
      ) : bugStats ? (
        <>
          <table className="defects-table">
            <thead>
              <tr>
                <th>Total Opened Bugs</th>
                <th>Total Closed Bugs</th>
                <th>Start Week</th>
                <th>End Week</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{bugStats.totalOpenedBugs || 0}</td>
                <td>{bugStats.totalClosedBugs || 0}</td>
                <td>{bugStats.startWeek}</td>
                <td>{bugStats.endWeek}</td>
              </tr>
            </tbody>
          </table>

          
          <div className="benchmark-section">
            <button
              className="add-benchmark-button"
              onClick={() => setShowBenchmarkModal(true)}
            >
              Add Benchmark
            </button>
          </div>

          
          <div className="graph-container">
            <div className="graph-section">
              <h3>Defect Metrics Chart</h3>
              <DefectMetricsChart data={bugStats} />
            </div>

            <div className="graph-section">
              <h3>Defects Removed Percentage Angainst Benchmark Trend</h3>
              <DefectsHistoryPercentageTrend githubUrl={githubUrl} />
            </div>

          </div>

          
          {showBenchmarkModal && (
            <div className="benchmark-modal">
              <div className="benchmark-modal-content">
                <button
                  className="close-modal"
                  onClick={() => setShowBenchmarkModal(false)}
                >
                  X
                </button>
                <Benchmarks githubUrl={githubUrl} selectedMetric="defects-removed" />
              </div>
            </div>
          )}
        </>
      ) : (
        <p>Loading bug statistics...</p>
      )}
    </div>
  );
};

export default DefectsRemoved;
