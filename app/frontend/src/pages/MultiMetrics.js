import React from "react";
import { useLocation } from "react-router-dom";
import FogIndexCalculator from "../components/FogIndexCalculator";
import DefectsRemoved from "../pages/DefectsRemoved";
import CodeComment from "../components/CodeComment";
import "../components/css/MultiMetrics.css"; 
import TestChurnDisplay from "../components/TestChurnDisplay";

const MultiMetrics = () => {
  const location = useLocation();
  const { selectedMetrics, githubUrl, owner, repo } = location.state || {}; 

  return (
    <div className="multi-metrics-container">
      <h2 className="multi-metrics-title">Multi-Metrics Dashboard</h2>

      {selectedMetrics?.length > 0 ? (
        <>
          {selectedMetrics.includes("fog-index") && <FogIndexCalculator githubUrl={githubUrl} />}
          {selectedMetrics.includes("code-comment-coverage") && <CodeComment selectedRepo={githubUrl} />}
          {selectedMetrics.includes("defects-removed") && <DefectsRemoved owner={owner} repo={repo} />}
          {selectedMetrics.includes("test-churn") && <TestChurnDisplay owner={owner} repo={repo} /> }
        </>
      ) : (
        <p className="no-metrics-selected">No metrics selected.</p>
      )}
    </div>
  );
};

export default MultiMetrics;
