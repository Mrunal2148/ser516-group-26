import React from "react";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";

const DefectMetricsChart = ({ data }) => {
  if (!data) return <p>No data available</p>;

  const weeks = Object.keys(data.weeklyClosedBugs);
  const closedBugs = Object.values(data.weeklyClosedBugs);
  const openedBugs = Object.values(data.weeklyOpenedBugs);

  const chartData = {
    labels: weeks,
    datasets: [
      {
        label: "Closed Bugs",
        data: closedBugs,
        backgroundColor: "rgba(255, 99, 132, 0.6)",
      },
      {
        label: "Opened Bugs",
        data: openedBugs,
        backgroundColor: "rgba(54, 162, 235, 0.6)",
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Weeks of the Year",  // Meaningful X-axis label
          font: {
            size: 14,
            weight: "bold",
          },
        },
      },
      y: {
        title: {
          display: true,
          text: "Number of Bugs",  // Meaningful Y-axis label
          font: {
            size: 14,
            weight: "bold",
          },
        },
      },
    },
  };

  return (
    <div style={{ width: "80%", margin: "auto" }}>
      <h3>Defect Metrics Chart</h3>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default DefectMetricsChart;
