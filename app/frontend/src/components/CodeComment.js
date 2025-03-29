import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import CoverageDashboard from "./CoverageDashboard";
import Benchmarks from "./Benchmarks";
import "../components/css/CodeComment.css";

export default function CodeComment() {
  const location = useLocation();
  const { githubUrl, metric } = location.state || {};
  const [coverage, setCoverage] = useState(null);
  const [coverageHistory, setCoverageHistory] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [showBenchmarkModal, setShowBenchmarkModal] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!githubUrl) return;



    // Fetch code comment coverage (Port 5006)
    const analyzeCoverage = async () => {
      try {
        const response = await axios.post("http://localhost:5006/analyze", { repo_url: githubUrl });
        setCoverage(response.data.coverage);
      } catch (error) {
        console.error("Error analyzing repository:", error);
        setError("❌ Failed to analyze repository coverage.");
      }
    };

    // Fetch past coverage history (Port 5006)
    const fetchCoverageHistory = async () => {
      try {
        const historyResponse = await axios.get("http://localhost:5006/get_coverage_data");
        const filteredData = historyResponse.data.filter((entry) => entry.repo_url === githubUrl);
        setCoverageHistory(filteredData);
      } catch (error) {
        console.error("Error fetching coverage history:", error);
        setError("❌ Failed to fetch coverage history.");
      }
    };

    // Fetch benchmark data (Port 5005)
    const fetchBenchmarks = async () => {
      try {
        const response = await axios.get("http://localhost:5005/benchmarks.json");
        if (Array.isArray(response.data)) {
          console.log("✅ Benchmarks Fetched in `CodeComment.js`:", benchmarks);
          setBenchmarks(response.data);
        } else {
          throw new Error("Invalid benchmark data format.");
        }
      } catch (error) {
        console.error("Error fetching benchmarks:", error);
        setError("❌ Failed to fetch benchmarks.");
      }
    };

    analyzeCoverage();
    fetchCoverageHistory();
    fetchBenchmarks();

  }, [githubUrl]);

  return (
      <div className="code-comment-container card">
        <h2 className="code-comment-title">Code Comment Coverage</h2>
        <p className="code-comment-repo">
          <b>Repository:</b>{" "}
          <a href={githubUrl} target="_blank" rel="noopener noreferrer">
            {githubUrl}
          </a>
        </p>

        {error && <p className="error-message">{error}</p>}

        {coverage !== null ? (
            <>
              <table className="code-comment-table">
                <thead>
                <tr>
                  <th>Metric</th>
                  <th>Value</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td>Comment Coverage</td>
                  <td>{coverage.toFixed(2)}%</td>
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
                <CoverageDashboard selectedRepo={githubUrl} benchmarks={benchmarks}/>
              </div>



              {showBenchmarkModal && (
                  <div className="benchmark-modal">
                    <div className="benchmark-modal-content">
                      <button className="close-modal" onClick={() => setShowBenchmarkModal(false)}>X</button>
                      <Benchmarks githubUrl={githubUrl} selectedMetric={metric || "code-comment-coverage"}/>
                    </div>
                  </div>
              )}
            </>
        ) : (
            <p className="mt-4 text-lg">🔍 Analyzing coverage...</p>
        )}
      </div>
  );
}
