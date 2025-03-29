import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../components/css/DefectsRemoved.css";
import DefectMetricsChart from "../components/DefectMetricsChart";
import DefectsHistoryPercentageTrend from "../components/DefectsHistoryPercentageTrend";
import DefectsBenchmarkTrend from "../components/DefectsBenchmarkTrend";
import Benchmarks from "../components/Benchmarks";

const DefectsRemoved = () => {
  const location = useLocation();
  const { owner, repo } = location.state || {};

  const [bugStats, setBugStats] = useState(null);
  const [error, setError] = useState(null);
  const [selectedGraph, setSelectedGraph] = useState("");
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
        setBugStats(data);
        setError(null);
      })
      .catch((error) => setError(error.message));
  }, [owner, repo]);

  const githubUrl = owner && repo ? `https://github.com/${owner}/${repo}` : "";

  
  const sortWeeks = (weeks) => {
    return weeks
      .map((week) => {
        const [year, weekNum] = week.split("-W").map(Number);
        return { week, year, weekNum };
      })
      .sort((a, b) => a.year - b.year || a.weekNum - b.weekNum)
      .map((obj) => obj.week);
  };

  
  const sortedOpenedWeeks =
    bugStats?.weeklyOpenedBugs ? sortWeeks(Object.keys(bugStats.weeklyOpenedBugs)) : [];
  const sortedClosedWeeks =
    bugStats?.weeklyClosedBugs ? sortWeeks(Object.keys(bugStats.weeklyClosedBugs)) : [];

  const startWeek = sortedOpenedWeeks.length > 0 ? sortedOpenedWeeks[0] : "N/A";
  const endWeek = sortedClosedWeeks.length > 0 ? sortedClosedWeeks[sortedClosedWeeks.length - 1] : "N/A";

  return (
    <div className="defects-container">
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
                <td>{startWeek}</td>
                <td>{endWeek}</td>
              </tr>
            </tbody>
          </table>

          
          <div className="chart-dropdown-container">
            <div className="dropdown-section">
              <select onChange={(e) => setSelectedGraph(e.target.value)} className="chart-select">
                <option value="">Select Graph Type</option>
                <option value="defectMetrics">Defect Metrics Chart</option>
                <option value="percentageTrend">Percentage Trend Over Time</option>
                <option value="DefectsBenchmarkTrend">Defects Benchmark Trend</option>
              </select>
            </div>
          </div>

         
          <div className="benchmark-section">
            <button 
              className="add-benchmark-button" 
              onClick={() => setShowBenchmarkModal(true)}
            >
              Add Benchmark
            </button>
          </div>

          
          {selectedGraph && (
            <div className="graph-container">
              {selectedGraph === "defectMetrics" && <DefectMetricsChart data={bugStats} />}
              {selectedGraph === "percentageTrend" && <DefectsHistoryPercentageTrend githubUrl={githubUrl} />}
              {selectedGraph === "DefectsBenchmarkTrend" && <DefectsBenchmarkTrend githubUrl={githubUrl} />}
            </div>
          )}

          
          {showBenchmarkModal && (
            <div className="benchmark-modal">
              <div className="benchmark-modal-content">
                <button className="close-modal" onClick={() => setShowBenchmarkModal(false)}>X</button>
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
