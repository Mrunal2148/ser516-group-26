import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import PropTypes from "prop-types";
import "../components/css/DefectTriage.css";
import { useLocation } from "react-router-dom";

const DefectsTriaged = () => {
  const location = useLocation();
  const { githubUrl, owner, repo } = location.state || {};
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!owner || !repo) {
      console.warn("Invalid GitHub repo info");
      return;
    }

    const fetchZipAndStats = async () => {
      try {
        const zipRes = await fetch("http://localhost:8003/fetch-repo", {
          method: "POST",
          body: JSON.stringify({ owner, repo, path: "" }),
          headers: { "Content-Type": "application/json" },
        });

        if (!zipRes.ok) throw new Error("Failed to fetch repo zip");

        const statsRes = await fetch(
          `http://localhost:8005/metrics/defects-triaged?owner=${owner}&repo=${repo}`,
          { method: "GET", headers: { "Content-Type": "application/json" } }
        );

        if (!statsRes.ok) throw new Error("Failed to fetch defect stats");

        const statsData = await statsRes.json();
        setStats(statsData);
      } catch (err) {
        console.error("Error:", err.message);
        setError("Failed to fetch defect metrics. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchZipAndStats();
  }, [githubUrl, owner, repo]);

  if (loading) return <p>Loading Defects Triaged metrics...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!stats) return <p>No data available.</p>;

  const {
    total_defects,
    triaged_defects,
    triaged_percentage,
    open_defects,
    closed_defects,
    by_severity = {},
  } = stats;

  // Format data for chart
  const severityData = Object.entries(by_severity).map(([severity, count]) => ({
    severity,
    total: count,
    triaged: count, // Update this if you later separate triaged vs. total by severity
  }));

  return (
    <div className="defects-triaged-container">
      <h3>Defect Triage Overview</h3>
      <div className="stats-overview">
        <p><strong>Total Defects:</strong> {total_defects}</p>
        <p><strong>Triaged Defects:</strong> {triaged_defects}</p>
        <p><strong>Triaged %:</strong> {triaged_percentage}%</p>
        <p><strong>Open:</strong> {open_defects}</p>
        <p><strong>Closed:</strong> {closed_defects}</p>
      </div>

      <h4>Defects by Severity</h4>
      {severityData.length ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={severityData} margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="severity" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#8884d8" name="Total Defects" />
            <Line type="monotone" dataKey="triaged" stroke="#82ca9d" name="Triaged Defects" />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p>No severity breakdown available.</p>
      )}
    </div>
  );
};

DefectsTriaged.propTypes = {
  githubUrl: PropTypes.string,
  owner: PropTypes.string,
  repo: PropTypes.string,
};

export default DefectsTriaged;
