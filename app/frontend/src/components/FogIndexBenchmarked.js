import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const BenchmarkedChart = ({ repoUrl }) => {
  const [historyData, setHistoryData] = useState([]);
  const [benchmarkHistory, setBenchmarkHistory] = useState([]);

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

  useEffect(() => {
    const fetchBenchmarkHistory = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5005/benchmarks.json");
        const data = await response.json();
        console.log("Fetched benchmark data:", data);
        const benchmark = data.find(b => b.repoUrl === repoUrl && b.metric === "fog-index");
        if (benchmark) {
          console.log("Benchmark history:", benchmark.history);
          setBenchmarkHistory(benchmark.history);
        } else {
          console.log("No matching benchmark found");
        }
      } catch (error) {
        console.error("Error fetching benchmark history:", error);
      }
    };

    fetchBenchmarkHistory();
  }, [repoUrl]);

  const labels = [...new Set([...historyData.map(item => item.generatedTime), ...benchmarkHistory.map(item => item.time)])].sort();

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
      {
        label: "Benchmark Fog Index",
        data: labels.map(label => {
          const item = benchmarkHistory.find(d => d.time === label);
          return item ? item.value : null;
        }),
        fill: false,
        borderColor: "orange",
        spanGaps: true,
      },
    ],
  };

  return <Line data={data} />;
};

export default BenchmarkedChart;
