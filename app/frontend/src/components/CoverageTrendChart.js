import React from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const CoverageTrendChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <p>No coverage data available for trend analysis.</p>;
  }

  // Sort data by timestamp
  const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const chartData = {
    labels: sortedData.map((entry) => new Date(entry.timestamp).toLocaleString()), // X-axis (time)
    datasets: [
      {
        label: "Code Comment Coverage Over Time",
        data: sortedData.map((entry) => entry.coverage), // Y-axis (coverage %)
        borderColor: "#007bff",
        backgroundColor: "rgba(0, 123, 255, 0.5)",
        fill: true,
        tension: 0.3, // Smooth curve
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: "Timestamp",
        },
        ticks: {
          maxTicksLimit: 6, // Avoid cluttering
        },
      },
      y: {
        title: {
          display: true,
          text: "Coverage (%)",
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ height: "400px", width: "100%" }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default CoverageTrendChart;
