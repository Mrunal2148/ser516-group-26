import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const CombinedCoverageChart = ({ data, githubUrl, benchmarks }) => {
  if (!data || data.length === 0 || benchmarks.length === 0) {
    return <p>No coverage or benchmark data available.</p>;
  }

  const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const sortedBenchmarks = [...benchmarks].sort((a, b) => new Date(a.time) - new Date(b.time));

  const chartData = {
    labels: sortedData.map((entry) => new Date(entry.timestamp).toLocaleString()), 
    datasets: [
      {
        label: "Code Comment Coverage Over Time (Line)",
        data: sortedData.map((entry) => entry.coverage), 
        borderColor: "#007bff",
        backgroundColor: "rgba(0, 123, 255, 0.5)",
        fill: false,
        tension: 0.3, 
        yAxisID: "y1", 
      },
      {
        label: "Benchmark Coverage Line",
        data: sortedData.map((entry) => {
          const benchmark = sortedBenchmarks.find(
            (b) => new Date(b.time).getTime() === new Date(entry.timestamp).getTime()
          );
          return benchmark ? benchmark.value : null; 
        }),
        borderColor: "rgba(255, 99, 132, 1)", 
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        fill: false,
        borderDash: [5, 5], 
        yAxisID: "y1", 
      },
      {
        label: "Coverage as Bar Chart",
        data: sortedData.map((entry) => entry.coverage), 
        backgroundColor: "rgba(82, 202, 157, 0.7)",
        yAxisID: "y2", 
        type: "bar", 
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
          maxTicksLimit: 6, 
        },
      },
      y1: {
        title: {
          display: true,
          text: "Coverage (%) (Line)",
        },
        beginAtZero: true,
        position: "left",
      },
      y2: {
        title: {
          display: true,
          text: "Coverage (%) (Bar)",
        },
        beginAtZero: true,
        position: "right",
        grid: {
          drawOnChartArea: false, 
        },
      },
    },
  };

  return (
    <div style={{ height: "400px", width: "100%" }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default CombinedCoverageChart;
