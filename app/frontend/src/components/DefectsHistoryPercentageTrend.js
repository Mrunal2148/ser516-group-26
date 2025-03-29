import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";
import axios from "axios";

const DefectsHistoryPercentageTrend = ({ githubUrl }) => {
    const [data, setData] = useState([]);
    const [benchmarkData, setBenchmarkData] = useState([]);

    useEffect(() => {
        if (!githubUrl) return;

        axios
            .get("http://localhost:8080/api/github/defects-history")
            .then((response) => {
                const repoName = githubUrl.split("/").pop();
                const filteredData = response.data.filter(entry => entry.repo_url.toLowerCase() === repoName.toLowerCase());
                setData(filteredData);
            })
            .catch((error) => console.error("Error fetching defect history:", error));

        axios
            .get("http://localhost:5005/benchmarks.json")
            .then((response) => {
                const filteredBenchmarks = response.data.find(
                    (entry) => entry.repoUrl.toLowerCase() === githubUrl.toLowerCase() &&
                        entry.metric === "defects-removed"
                );
                setBenchmarkData(filteredBenchmarks ? filteredBenchmarks.history : []);
            })
            .catch((error) => console.error("Error fetching benchmark history:", error));
    }, [githubUrl]);

    if (!githubUrl) {
        return <p style={{ color: "red", fontWeight: "bold" }}>No repository selected.</p>;
    }

    if (!data.length && !benchmarkData.length) {
        return <p>No historical data available for <b>{githubUrl}</b>.</p>;
    }

    const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const sortedBenchmarkData = [...benchmarkData].sort((a, b) => new Date(a.time) - new Date(b.time));

    const labels = [...new Set([
        ...sortedData.map(entry => new Date(entry.timestamp).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })),
        ...sortedBenchmarkData.map(entry => new Date(entry.time).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }))
    ])];

    const percentageClosed = sortedData.map(entry => entry.percentage_bugs_closed);
    const benchmarkValues = sortedBenchmarkData.map(entry => entry.value);

    const datasets = [
        {
            label: "Defects Closed (%)",
            data: percentageClosed,
            borderColor: "#007bff",
            backgroundColor: "rgba(0, 123, 255, 0.2)",
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 5,
            pointBackgroundColor: "#007bff",
            pointBorderWidth: 2,
            pointHoverRadius: 7,
        },
        {
            label: "Benchmark Trend",
            data: benchmarkValues.length ? benchmarkValues : Array(labels.length).fill(null),
            borderColor: "#ff5733",
            backgroundColor: "rgba(255, 87, 51, 0.3)",
            fill: false,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 5,
            pointBackgroundColor: "#ff5733",
            pointBorderWidth: 2,
            pointHoverRadius: 7,
            borderDash: [5, 5],
        }
    ];

    const chartData = {
        labels: labels,
        datasets: datasets,
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: "top",
                labels: {
                    color: "#333",
                    font: {
                        size: 14,
                        weight: "bold",
                    },
                },
            },
            tooltip: {
                backgroundColor: "rgba(0, 0, 0, 0.8)",
                titleFont: { size: 14, weight: "bold" },
                bodyFont: { size: 13 },
                bodySpacing: 6,
                padding: 10,
                displayColors: false,
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "Timestamp",
                    font: { size: 14, weight: "bold" },
                },
                ticks: {
                    color: "#555",
                    font: { size: 12 },
                    maxRotation: 30,
                    minRotation: 30,
                    autoSkip: true,
                    maxTicksLimit: 8,
                },
                grid: {
                    display: true,
                },
            },
            y: {
                title: {
                    display: true,
                    text: "Percentage Bugs Closed (%)",
                    font: { size: 14, weight: "bold" },
                },
                ticks: {
                    color: "#555",
                    font: { size: 12 },
                    stepSize: 10,
                    beginAtZero: true,
                    min: 0,
                    max: 100,
                    callback: function (value) {
                        return value + "%";
                    },
                },
                grid: {
                    color: "rgba(200, 200, 200, 0.3)",
                },
            },
        },
    };

    return (
        <div style={{ height: "100%" }}>
             {benchmarkValues.length === 0 && (
        <p style={{ padding: 8, fontWeight: "bold", color: "red" }}>
          No benchmark data available. Please add benchmarks and reload the page to see the Benchmark over Time graph.
        </p>
      )}
            <Line data={chartData} options={options} />
        </div>
    );
};

export default DefectsHistoryPercentageTrend;
