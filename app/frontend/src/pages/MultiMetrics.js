import React from "react";
import { useLocation } from "react-router-dom";
import FogIndexCalculator from "../components/FogIndexCalculator";
import DefectsRemoved from "../pages/DefectsRemoved";
import CodeComment from "../components/CodeComment";
import TestChurnDisplay from "../components/TestChurnDisplay";
import MetricsForm from "../components/MetricsForm";
import "../components/css/MultiMetrics.css";

const MultiMetrics = () => {
  const location = useLocation();
  const { selectedMetrics, githubUrl, owner, repo } = location.state || {};

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

        {(selectedMetrics.includes("fan-in-fan-out"))&& (
            <MetricsForm githubUrl={githubUrl} owner={owner} repo={repo} />
          )}
        </>
      ) : (
        <p className="no-metrics-selected">No metrics selected.</p>
      )}
    </div>
  );
};

export default MultiMetrics;
