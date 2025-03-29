import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const CombinedCoverageChart = ({ data, githubUrl, benchmarks }) => {
  const [benchmarkDataset, setBenchmarkDataset] = useState([]);

  useEffect(() => {
    if (!data || data.length === 0 || !benchmarks || benchmarks.length === 0) {
      return;
    }

    const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const repoBenchmarks = benchmarks.find((b) => b.repoUrl === githubUrl && b.metric === "code-comment-coverage");

    if (!repoBenchmarks || !Array.isArray(repoBenchmarks.history) || repoBenchmarks.history.length === 0) {
      return;
    }

    const newBenchmarkDataset = sortedData.map((entry) => {
      const coverageTime = new Date(entry.timestamp).getTime();

      const pastBenchmarks = repoBenchmarks.history.filter(
          (benchmark) => new Date(benchmark.time).getTime() <= coverageTime
      );

      const latestBenchmark = pastBenchmarks.length > 0 ? pastBenchmarks[pastBenchmarks.length - 1].value : null;

      return latestBenchmark;
    });

    setBenchmarkDataset(newBenchmarkDataset);
  }, [data, benchmarks]);

  const chartData = {
    labels: data.map((entry) => new Date(entry.timestamp).toLocaleString("en-US", { timeZone: "UTC" })),
    datasets: [
      {
        label: "Benchmark Coverage",
        data: benchmarkDataset,
        borderColor: "rgba(255, 99, 132, 1)",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        fill: false,
        borderWidth: 2,
        pointRadius: 4,
      },
      {
        label: "Code Comment Coverage (%) Over Time",
        data: data.map((entry) => entry.coverage * 100),
        borderColor: "#007bff",
        backgroundColor: "rgba(0, 123, 255, 0.5)",
        fill: false,
        tension: 0.3,
      }
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          font: { size: 14 },
          padding: 15,
        },
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Timestamp (UTC)",
          font: { size: 14, weight: "bold" },
        },
        ticks: {
          maxTicksLimit: 6,
          autoSkip: true,
        },
      },
      y: {
        title: {
          display: true,
          text: "Coverage (%)",
          font: { size: 14, weight: "bold" },
        },
        beginAtZero: true,
        suggestedMax: 100,
      }
    },
  };

  return (
      <div style={{ height: "100%" }}> {/* Add fixed height */}
         {benchmarkDataset.length === 0 && (
        <p style={{ padding: 5, fontWeight: "bold", color: "red" }}>
          No benchmark data available. Please add benchmarks and reload the page to see the Benchmark over Time graph.
        </p>
      )}
        <p style={{ padding: 5, textAlign: "center", fontSize: "14px", color: "#555" }}>
          Note: All timestamps are in UTC.
        </p>

        <Line data={chartData} options={options} />
      </div>
  );
};

export default CombinedCoverageChart;



