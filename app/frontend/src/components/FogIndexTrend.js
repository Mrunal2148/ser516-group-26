import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TrendChart = ({ repoUrl }) => {
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const truncatedUrl = repoUrl.replace("/archive/refs/heads/main.zip", "");
        console.log("Fetching history for:", truncatedUrl);

        const response = await fetch(`http://127.0.0.1:8080/api/fog-index/history?repoUrl=${encodeURIComponent(truncatedUrl)}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch history: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Fetched history data:", data);

        setHistoryData(data);
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };

    fetchHistory();
  }, [repoUrl]);

  const labels = [...new Set([...historyData.map(item => item.generatedTime)])].sort();

  const data = {
    labels: labels.map(label => {
      const date = new Date(label);
      console.log(`Parsing date: ${label} -> ${date}`); // Log the date parsing
      return date.toLocaleString();
    }),
    datasets: [
      {
        label: "Fog Index",
        data: labels.map(label => {
          const item = historyData.find(d => d.generatedTime === label);
          return item ? item.fogIndex : null;
        }),
        fill: false,
        borderColor: "blue",
        spanGaps: true,
      },
    ],
  };

  return <Line data={data} />;
};

export default TrendChart;
