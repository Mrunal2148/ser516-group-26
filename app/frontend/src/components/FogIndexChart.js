import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const FogIndexChart = ({ data }) => {
  if (!data) return <p>No data available</p>;

  const chartData = {
    labels: ["Fog Index Metrics"],
    datasets: [
      {
        label: "Percentage of Complex Words (%)",
        data: [data.percentageComplexWords || 0],
        backgroundColor: "rgba(255, 99, 132, 0.6)",
        yAxisID: "y-left",
      },
      {
        label: "Average Sentence Length",
        data: [data.averageSentenceLength || 0],
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        yAxisID: "y-left",
      },
      {
        label: "Fog Index",
        data: [data.fogIndex || 0],
        type: "line",
        borderColor: "rgba(255, 206, 86, 1)",
        backgroundColor: "rgba(255, 206, 86, 0.6)",
        borderWidth: 4, // 🔥 Increased for better visibility
        pointRadius: 8, // 🔥 Enlarged point size for visibility
        pointBackgroundColor: "rgba(255, 206, 86, 1)", // Ensures points are visible
        pointBorderColor: "black",
        pointBorderWidth: 2,
        yAxisID: "y-right",
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
      "y-left": {
        type: "linear",
        position: "left",
        beginAtZero: true,
        title: {
          display: true,
          text: "Percentage Complex Words / Avg Sentence Length",
        },
      },
      "y-right": {
        type: "linear",
        position: "right",
        beginAtZero: true,
        title: {
          display: true,
          text: "Fog Index (Readability Complexity)",
        },
        grid: {
          drawOnChartArea: false, // Only show grid for left axis
        },
      },
    },
  };

  return (
    <div style={{ width: "80%", margin: "auto" }}>
      <h3>Fog Index Complexity Breakdown</h3>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default FogIndexChart;
