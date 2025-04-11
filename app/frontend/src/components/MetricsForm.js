import React, { useEffect, useState } from "react";
import "../components/css/MetricsForm.css";

const token = process.env.REACT_APP_GITHUB_TOKEN;

const MetricsForm = ({ githubUrl }) => {
  const [zipFile, setZipFile] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  // Get the repository name for display purposes.
  const repoName = githubUrl?.replace("https://github.com/", "");

  useEffect(() => {
    if (!githubUrl) return;

    const fetchZip = async () => {
      try {
        // Using the full repo URL, extract owner and repo from it.
        const parts = githubUrl.split("/");
        const owner = parts[3]; // Adjust based on the URL structure, e.g., "https://github.com/owner/repo"
        const repo = parts[4];

        let data = null;
        for (const branch of ["main", "master"]) {
          const res = await fetch("http://localhost:8003/fetch-repo", {
            method: "POST",
            body: JSON.stringify({
              owner: owner,
              repo: repo,
              branch: branch,
              token: token,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          });

          if (res.ok) {
            data = await res.json();
            break;
          } else {
            console.warn(`Failed to fetch with branch ${branch}: ${res.status}`);
          }
        }

        if (!data) {
          throw new Error("Failed to fetch ZIP from GitHub on both main and master");
        }

        setAvailableFiles(data.files || []);
        setZipFile(data.zip_path); // Use zip_path from the backend
      } catch (err) {
        console.error("Fetch error:", err.message);
        setError("Failed to fetch GitHub ZIP. Try Again!");
      }
    };

    fetchZip();
  }, [githubUrl]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!zipFile) {
      setError("No ZIP file available. Ensure the repository is fetched.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("folder", zipFile);
      formData.append("scope", "{}");

      const res = await fetch("http://localhost:8000/metrics/combined-scoped-multi", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Metric calculation failed");

      setResults(data.results);
    } catch (err) {
      setError(err.message || "Failed to calculate metrics");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="metric-form-container">
      <h3>Fan-In / Fan-Out Metrics</h3>
      {repoName && (
        <p style={{ fontSize: "14px", marginTop: "4px", marginBottom: "10px" }}>
          <strong>Repository:</strong>{" "}
          <a href={githubUrl} target="_blank" rel="noopener noreferrer">
            {repoName}
          </a>
        </p>
      )}

      {error && <p className="text-red-600">{error}</p>}
      {loading && <p>Calculating metrics...</p>}

      {availableFiles.length > 0 && (
        <form onSubmit={handleSubmit}>
          <div>
            <p>{availableFiles.length} Java files found.</p>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Calculating..." : "Calculate Metrics"}
          </button>
        </form>
      )}

      {results && (
        <div className="results">
          {Object.entries(results).map(([method, data]) => (
            <div key={method}>
              <strong>{method}</strong>
              <p>Fan-in: {data.total_fan_in ?? data.fan_in}</p>
              <p>Fan-out: {data.total_fan_out ?? data.fan_out}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MetricsForm;
