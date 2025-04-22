import React, { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import PropTypes from "prop-types";
import "../components/css/DefectTriage.css";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const DefectsTriaged = ({ githubUrl }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Parse owner and repo from GitHub URL
  const repoName = githubUrl?.replace("https://github.com/", "");
  const parts = githubUrl?.split("/");
  const owner = parts?.[3];
  const repo = parts?.[4];

  useEffect(() => {
    if (!owner || !repo) {
      setError("Invalid GitHub repository URL.");
      setLoading(false);
      return;
    }

    const fetchStats = async () => {
      try {
        const url = `http://defects-triaged-service:8000/metrics/defects-triaged?owner=${owner}&repo=${repo}`;
        const response = await fetch(url);
        if (!response.ok)
          throw new Error(`Error fetching metrics: ${response.statusText}`);
        const data = await response.json();
        setStats(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [owner, repo]);

  if (loading) return <p>Loading Defects Triaged metrics...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!stats) return <p>No data available.</p>;

  // ✅ This is now safe because we're checking that stats is not null above
  const triaged = stats.triaged_defects || 0;
  const untriaged = (stats.total_defects ?? 0) - triaged;

  const pieData = [
    { name: "Triaged", value: triaged },
    { name: "Untriaged", value: untriaged },
  ];

  return (
    <div className="defects-triaged-container">
      <h3>Defects Triaged Overview</h3>
      {repoName && (
        <p style={{ fontSize: "14px", marginTop: "4px", marginBottom: "10px" }}>
          <strong>Repository:</strong>{" "}
          <a href={githubUrl} target="_blank" rel="noopener noreferrer">
            {repoName}
          </a>
        </p>
      )}
      <div className="stats-overview">
        <p>
          <strong>Triaged:</strong> {triaged}
        </p>
        <p>
          <strong>Untriaged:</strong> {untriaged}
        </p>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label={({ name, percent }) =>
              `${name}: ${Math.round(percent * 100)}%`
            }
          >
            {pieData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value) => value} />
          <Legend verticalAlign="bottom" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

DefectsTriaged.propTypes = {
  githubUrl: PropTypes.string.isRequired,
};

export default DefectsTriaged;
