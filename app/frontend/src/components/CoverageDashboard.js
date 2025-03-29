import React, { useEffect, useState } from "react";
import axios from "axios";
import CoverageChart from "./CoverageChart";
import CombinedCoverageChart from "./CombinedCoverageChart";

const CoverageDashboard = ({ selectedRepo, benchmarks }) => {
    const [chartData, setChartData] = useState([]);
    const [historyData, setHistoryData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!selectedRepo) return;

        setLoading(true);
        setError(null);

        axios.get("http://localhost:5006/get_coverage_data")
            .then(response => {
                const repoData = response.data.find(repo => repo.repo_url === selectedRepo);
                const history = response.data.filter(repo => repo.repo_url === selectedRepo);

                if (repoData) {
                    setChartData([
                        { name: "Total Lines", value: repoData.total_lines },
                        { name: "Comment Lines", value: repoData.comment_lines },
                        // { name: "Coverage %", value: repoData.coverage },
                    ]);
                } else {
                    setChartData([]);
                }

                setHistoryData(history);
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching coverage data:", error);
                setError("Error fetching coverage data");
                setLoading(false);
            });
    }, [selectedRepo]);

    return (
        <div style={{ width: "100%", padding: "20px" }}>
            {/* <h2>Code Comment Coverage Breakdown</h2> */}

            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : chartData.length > 0 ? (
                <div className="graph-container-comment">
                    <div className="graph-section-comment">
                        <h3>Coverage Breakdown</h3>
                        <CoverageChart chartData={chartData} />
                    </div>

                    <div className="graph-section-comment">
                        <h3>Benchmark Comparison Over Time</h3>
                        <CombinedCoverageChart data={historyData} githubUrl={selectedRepo} benchmarks={benchmarks} />
                    </div>
                </div>
            ) : (
                <p>No coverage data available for this repository.</p>
            )}
        </div>
    );
};

export default CoverageDashboard;
