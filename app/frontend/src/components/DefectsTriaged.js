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
  const { owner, repo } = location.state || {};
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!owner || !repo) {
      console.warn("Invalid GitHub repo info");
      return;
    }

    const fetchDefectStats = async () => {
      try {
        const statsRes = await fetch(
          `http://localhost:8005/metrics/defects-triaged?owner=${owner}&repo=${repo}`,
          { method: "GET", headers: { "Content-Type": "application/json" } }
        );

        if (!statsRes.ok) throw new Error("Failed to fetch defect stats");

        const statsData = await statsRes.json();
        console.log("Fetched stats:", statsData);  // Add this log
        setStats(statsData);
      } catch (err) {
        console.error("Error:", err.message);
        setError("Failed to fetch defect metrics. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchDefectStats();
  }, [owner, repo]);

  if (loading) return <p>Loading Defects Triaged metrics...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!stats) return <p>No data available.</p>;

  // Prepare a flat map from stats.data
  const defectMetrics = stats?.data?.defect_data?.reduce((acc, item) => {
    const key = item.class_name.toLowerCase().replace(/\s+/g, "_");
    acc[key] = item.score;
    return acc;
  }, {});

  // Extract time-series data from `data_by_day`
  const dataByDay = stats?.data?.data_by_day || [];

  // NEW: Extract by_severity and by_priority separately
  const by_severity = stats?.by_severity || {};
  const by_priority = stats?.by_priority || {};

  // Safely fallback if no data
  const {
    total_defects = 0,
    triaged_defects = 0,
    open_triaged_defects = 0,
    closed_triaged_defects = 0,
    defect_triaged_percentage = 0,
  } = defectMetrics || {};

  // Format data for severity chart
  const severityData = Object.entries(by_severity).map(([severity, count]) => ({
    severity,
    total: count,
    triaged: count, // Update this if triaged data is separated in the backend
  }));

  // Format data for priority chart (if available)
  const priorityData = Object.entries(by_priority).map(([priority, count]) => ({
    priority,
    total: count,
    triaged: count, // Adjust if priority is split between total/triaged
  }));

  // NEW: Open vs Closed vs Triaged data
  const openClosedData = [
    { status: "Open", count: open_triaged_defects },
    { status: "Closed", count: closed_triaged_defects },
    { status: "Triaged", count: triaged_defects },
  ];

  // Format data for the time-series chart
  const timeSeriesData = dataByDay.map((entry) => ({
    date: entry.date,
    open_defects: entry.open_defects,
    closed_defects: entry.closed_defects,
    triaged_defects: entry.triaged_defects,
  }));

  return (
    <div className="defects-triaged-container">
      <h3>Defect Triage Overview</h3>
      <div className="stats-overview">
        <p><strong>Total Defects:</strong> {total_defects}</p>
        <p><strong>Triaged Defects:</strong> {triaged_defects}</p>
        <p><strong>Triaged %:</strong> {defect_triaged_percentage}%</p>
        <p><strong>Open:</strong> {open_triaged_defects}</p>
        <p><strong>Closed:</strong> {closed_triaged_defects}</p>
      </div>

      <h4>Open vs Closed vs Triaged Defects</h4>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={openClosedData} margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="status" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="count" stroke="#8884d8" name="Defect Count" />
        </LineChart>
      </ResponsiveContainer>

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

      <h4>Defects by Priority</h4>
      {priorityData.length ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={priorityData} margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="priority" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#8884d8" name="Total Defects" />
            <Line type="monotone" dataKey="triaged" stroke="#82ca9d" name="Triaged Defects" />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p>No priority breakdown available.</p>
      )}

      <h4>Defects Over Time (Last 90 Days)</h4>
      {timeSeriesData.length ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeSeriesData} margin={{ top: 10, right: 30, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="open_defects" stroke="#8884d8" name="Open Defects" />
            <Line type="monotone" dataKey="closed_defects" stroke="#82ca9d" name="Closed Defects" />
            <Line type="monotone" dataKey="triaged_defects" stroke="#ff7300" name="Triaged Defects" />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p>No time-series data available.</p>
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
