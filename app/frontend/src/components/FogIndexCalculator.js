import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import FogIndexChart from "../components/FogIndexChart";
import BenchmarkedChart from "./FogIndexBenchmarked";
import Benchmarks from "../components/Benchmarks";
import "./css/FogIndexCalculator.css";

const FogIndexCalculator = () => {
  const location = useLocation();
  const { githubUrl } = location.state || {};

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [benchmarkHistory, setBenchmarkHistory] = useState([]);
  const [showBenchmarkModal, setShowBenchmarkModal] = useState(false);

  useEffect(() => {
    if (githubUrl) {
      calculateFogIndex(githubUrl);
      fetchHistory(githubUrl);
      fetchBenchmarkHistory(githubUrl, "fog-index");
    }
  }, [githubUrl]);

  const formatGitHubZipUrl = (repoUrl) => {
    if (!repoUrl) return "";
    if (repoUrl.endsWith(".zip")) return repoUrl;
    return repoUrl.replace(/\.git$/, "").replace(/\/$/, "") + "/archive/main.zip";
  };

  const calculateFogIndex = async (url) => {
    try {
      setLoading(true);
      setError(null);
      const zipUrl = formatGitHubZipUrl(url);

      const response = await fetch(
        `http://127.0.0.1:8080/api/fog-index/calculate?githubZipUrl=${encodeURIComponent(zipUrl)}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setError(error.message || "Failed to fetch the Fog Index");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (url) => {
    try {
      const truncatedUrl = url.replace("/archive/refs/heads/main.zip", "");
      console.log("Fetching history for:", truncatedUrl);

      const response = await fetch(`http://127.0.0.1:8080/api/fog-index/history?repoUrl=${encodeURIComponent(truncatedUrl)}`);
     
      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Fetched history data:", data);

      setHistory(data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const fetchBenchmarkHistory = async (url, metric) => {
    try {
      const response = await fetch("http://127.0.0.1:5005/benchmarks.json");
      const data = await response.json();
      console.log("Fetched benchmark data:", data);
      const benchmark = data.find(b => b.repoUrl === url && b.metric === metric);
      if (benchmark) {
        console.log("Benchmark history:", benchmark.history);
        setBenchmarkHistory(benchmark.history);
      } else {
        console.log("No matching benchmark found");
      }
    } catch (error) {
      console.error("Error fetching benchmark history:", error);
    }
  };

  return (
    <div className="fog-index-container card">
      <h2 className="code-comment-title">Fog Index Calculator</h2>

      {githubUrl && (
        <p className="fog-index-repo">
          <b>Repository:</b> <a href={githubUrl} target="_blank" rel="noopener noreferrer">{githubUrl}</a>
        </p>
      )}

      {loading && <p>Calculating Fog Index...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <>
          <table className="fog-index-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
        <tr>
          <td>Fog Index</td>
          <td>{result.fogIndex}</td>
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
              <h3>Fog Index Complexity Breakdown</h3>
              <FogIndexChart data={result} />
            </div>

            <div className="graph-section">
              <h3>Benchmark Comparison</h3>
              <BenchmarkedChart repoUrl={githubUrl} />
            </div>
          </div>

          
          {showBenchmarkModal && (
            <div className="benchmark-modal">
              <div className="benchmark-modal-content">
                <button className="close-modal" onClick={() => setShowBenchmarkModal(false)}>X</button>
                <Benchmarks githubUrl={githubUrl} selectedMetric="fog-index" />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default FogIndexCalculator;
