import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import FogIndexCalculator from "../components/FogIndexCalculator";
import DefectsRemoved from "../pages/DefectsRemoved";
import CodeComment from "../components/CodeComment";
import TestChurnDisplay from "../components/TestChurnDisplay";
import MetricsForm from "../components/MetricsForm";
import TestCoverage from "../components/TestCoverage";
import "../components/css/MultiMetrics.css";
import DefectsTriaged from "../components/DefectsTriaged"

const MultiMetrics = () => {
  const location = useLocation();
  const { selectedMetrics, githubUrl, owner, repo } = location.state || {};
  const [coverageReady, setCoverageReady] = useState(false);

  useEffect(() => {
    if (selectedMetrics?.includes("test-coverage") && githubUrl) {
      fetch(`http://localhost:8004/metrics/test-coverage?repo_url=${githubUrl}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.message && data.download_path) {
            setCoverageReady(true);
          }
        })
        .catch((err) => {
          console.error("Error fetching test coverage:", err);
        });
    }
  }, [selectedMetrics, githubUrl]);

  return (
    <div className="multi-metrics-container">
      <h2 className="multi-metrics-title">Multi-Metrics Dashboard</h2>

      {selectedMetrics?.length > 0 ? (
        <>
          {selectedMetrics.includes("fog-index") && (
            <section className="metric-section">
              <h3>FOG INDEX CALCULATOR</h3>
              <FogIndexCalculator githubUrl={githubUrl} />
            </section>
          )}

          {selectedMetrics.includes("code-comment-coverage") && (
            <section className="metric-section">
              <h3>CODE COMMENT COVERAGE</h3>
              <CodeComment selectedRepo={githubUrl} />
            </section>
          )}

          {selectedMetrics.includes("defects-removed") && (
            <section className="metric-section">
              <h3>DEFECTS REMOVED</h3>
              <DefectsRemoved owner={owner} repo={repo} />
            </section>
          )}

          {selectedMetrics.includes("test-churn") && (
            <section className="metric-section">
              <h3>TEST CHURN</h3>
              <TestChurnDisplay owner={owner} repo={repo} />
            </section>
          )}

          {selectedMetrics.includes("defects-triaged") && (
            <section className="metric-section">
              <h3>DEFECTS TRIAGED</h3>
              <DefectsTriaged githubUrl={githubUrl} owner={owner} repo={repo} />
            </section>
          )}

        {(selectedMetrics.includes("fan-in-fan-out"))&& (
            <MetricsForm githubUrl={githubUrl} owner={owner} repo={repo} />
          )}

          {selectedMetrics.includes("test-coverage") && (
            <section className="metric-section">
              <h3>TEST COVERAGE</h3>
              <TestCoverage githubUrl={githubUrl} />

              {coverageReady && (
                <button
                  className="download-button"
                  onClick={() => {
                    const link = document.createElement("a");
                    link.href = "http://localhost:8004/metrics/test-coverage-report/download";
                    link.download = "test_coverage_report.pdf";
                    link.click();
                  }}
                  style={{ marginTop: "10px" }}
                >
                  Download Test Coverage Report (PDF)
                </button>
              )}
            </section>
          )}
          
        </>
      ) : (
        <p className="no-metrics-selected">No metrics selected.</p>
      )}
    </div>
  );
};

export default MultiMetrics;
