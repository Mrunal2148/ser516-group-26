import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";
import axios from "axios";

const DefectsBenchmarkTrend = ({ githubUrl }) => {
    const [defectData, setDefectData] = useState([]);
    const [benchmarkData, setBenchmarkData] = useState([]);

    useEffect(() => {
        if (!githubUrl) return;

        // Extract repo name from the URL
        const repoName = githubUrl.split("/").pop();

        // Fetch defect history
        axios
            .get("http://localhost:8080/api/github/defects-history")
            .then((response) => {
                const filteredDefects = response.data.filter(entry => entry.repo_url.toLowerCase() === repoName.toLowerCase());
                setDefectData(filteredDefects);
            })
            .catch((error) => console.error("Error fetching defect history:", error));

        // Fetch benchmark data
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

    if (!defectData.length && !benchmarkData.length) {
        return <p>No historical data available for <b>{githubUrl}</b>.</p>;
    }

    // Sort defect data by timestamp
    const sortedDefectData = [...defectData].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const sortedBenchmarkData = [...benchmarkData].sort((a, b) => new Date(a.time) - new Date(b.time));

    // Labels (X-axis timestamps)
    const defectLabels = sortedDefectData.map(entry =>
        new Date(entry.timestamp).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    );
    const benchmarkLabels = sortedBenchmarkData.map(entry =>
        new Date(entry.time).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    );

    // Data points for Y-axis
    const defectPercentage = sortedDefectData.map(entry => entry.percentage_bugs_closed);
    const benchmarkValues = sortedBenchmarkData.map(entry => entry.value);

    const chartData = {
        labels: [...new Set([...defectLabels, ...benchmarkLabels])], 
        datasets: [
            {
                label: "Defects Removed (%)",
                data: defectPercentage,
                borderColor: "#007bff",
                backgroundColor: "rgba(0, 123, 255, 0.3)",
                fill: false,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: "#007bff",
                pointBorderWidth: 2,
                pointHoverRadius: 7,
            },
            {
                label: "Benchmark Trend",
                data: benchmarkValues,
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
            },
        ],
    };

    const options = {
        responsive: true,
        layout: {
            padding: {
                top: 20,
                bottom: 20,
            },
        },
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
                    padding: 15,
                },
            },
            tooltip: {
                backgroundColor: "rgba(0, 0, 0, 0.8)",
                titleFont: { size: 14, weight: "bold" },
                bodyFont: { size: 13 },
                bodySpacing: 6,
                padding: 12,
                displayColors: false,
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "Timestamp",
                    font: { size: 14, weight: "bold" },
                    padding: 10,
                },
                ticks: {
                    color: "#555",
                    font: { size: 12 },
                    maxRotation: 25,
                    minRotation: 25,
        
                    maxTicksLimit: 6,  
                },
                grid: {
                    display: true,  
                    color: "rgba(200, 200, 200, 0.3)",
                },
            },
            y: {
                title: {
                    display: true,
                    text: "Percentage Bugs Closed (%)",
                    font: { size: 14, weight: "bold" },
                    padding: 10,
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
                    color: "rgba(200, 200, 200, 0.5)",  
                    borderDash: [4, 4], 
                },
            },
        },
    };
    
    

    return (
        <div className="benchmark-trend-container">
           
            <div className="graph-container">
                <Line data={chartData} options={options} />
            </div>
        </div>
    );
};

export default DefectsBenchmarkTrend;
