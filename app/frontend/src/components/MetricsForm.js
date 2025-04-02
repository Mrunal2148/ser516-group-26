import React, { useEffect, useState } from "react";
import DirectoryTree from "./DirectoryTree";
import "../components/css/MetricsForm.css";

const MetricsForm = ({ githubUrl }) => {
  const [zipFile, setZipFile] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [functionNames, setFunctionNames] = useState([""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  const repoName = githubUrl?.replace("https://github.com/", "");

  useEffect(() => {
    if (!githubUrl) return;

    const zipUrl = `${githubUrl}/archive/refs/heads/main.zip`;
    const formData = new FormData();
    formData.append("githubZipUrl", zipUrl);

    const fetchZip = async () => {
      try {
        const res = await fetch("http://localhost:8001/github-zip", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) throw new Error("Failed to fetch ZIP from GitHub");

        const data = await res.json();
        setAvailableFiles(data.files);
        setZipFile(data.zipFileName);
      } catch (err) {
        console.error("Fetch error:", err.message);
        setError("Failed to fetch GitHub ZIP. Try Again !");
      }
    };

    fetchZip();
  }, [githubUrl]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!zipFile || selectedFiles.length === 0 || functionNames.every(name => name.trim() === "")) {
      setError("Please provide method name(s) and select files.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("folder", zipFile);
      formData.append("scope", JSON.stringify({
        selected_files: selectedFiles,
        function_names: functionNames,
      }));

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
      {loading && <p>Loading GitHub ZIP...</p>}

      {availableFiles.length > 0 && (
        <form onSubmit={handleSubmit}>
          <DirectoryTree
            files={availableFiles}
            selectedFiles={selectedFiles}
            onFileSelectionChange={setSelectedFiles}
          />

          <div className="method-inputs">
            {functionNames.map((name, idx) => (
              <input
                key={idx}
                type="text"
                value={name}
                placeholder="Enter method name"
                onChange={(e) => {
                  const updated = [...functionNames];
                  updated[idx] = e.target.value;
                  setFunctionNames(updated);
                }}
              />
            ))}
            <button type="button" onClick={() => setFunctionNames([...functionNames, ""])}>
              ➕ Add Method
            </button>
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
