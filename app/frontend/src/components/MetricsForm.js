import React, { useEffect, useState } from "react";
import DirectoryTree from "./DirectoryTree";
import "../components/css/MetricsForm.css";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import FanInFanOutChart from "./FanInFanOutChart";


const token = process.env.REACT_APP_GITHUB_TOKEN;

const MetricsForm = ({ githubUrl }) => {
  const [zipFile, setZipFile] = useState(null);
  const [availableFiles, setAvailableFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [functionNames, setFunctionNames] = useState([""]);
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
        const owner = parts[3]; // e.g., from "https://github.com/owner/repo"
        const repo = parts[4];
    
        // Remove the branch field so backend can determine it automatically.
        const res = await fetch("http://localhost:8003/fetch-repo", {
          method: "POST",
          body: JSON.stringify({
            owner,
            repo,
            token,        // Provide token if available; omit if not needed
            path: "",     // Include path if needed, or omit entirely if not used.
          }),
          headers: {
            "Content-Type": "application/json",
          },
        });
    
        if (!res.ok) throw new Error("Failed to fetch repo zip");
        const data = await res.json();
    

        if (!Array.isArray(data.files)) {
          console.error("data.files is not an array:", data.files);
          setError("Unexpected format for file list from the backend.");
          return;
        }
        console.log("Files from backend:", data.files); // Debugging

        // Format the files for the DirectoryTree component
        const formattedFiles = data.files.map((filePath) => ({
          path: filePath,
          name: filePath.split("/").pop(), // Extract file name from path
          type: "file",
        }));

        setAvailableFiles(formattedFiles || []);
        setZipFile(data.zip_path); // Use zip_path from the backend
        console.log("fetched data", data);
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
      const blob = await fetchZipFileAsBlob(zipFile);
      const fileObj = new File([blob], "repository.zip", { type: "application/zip" });

      const formData = new FormData();
      formData.append("folder", fileObj);
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
      console.log("Metric results:", data.results);
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
        <>
          <div className="results">
          <FanInFanOutChart
            data={Object.entries(results).map(([method, data]) => ({
              function: method,
              fanIn: data.total_fan_in ?? data.fan_in,
              fanOut: data.total_fan_out ?? data.fan_out,
            }))}
          />
        </div>
        </>
      )}
    </div>
  );
};

//helper function for zip files
const fetchZipFileAsBlob = async (zipFilePath) => {
  try {
    const res = await fetch(`http://localhost:8003/download?path=${encodeURIComponent(zipFilePath)}`);
    if (!res.ok) {
      throw new Error("Unable to download ZIP file.");
    }
    return await res.blob();
  } catch (error) {
    console.error("Error fetching ZIP file as blob:", error);
    throw error;
  }
};


export default MetricsForm;
