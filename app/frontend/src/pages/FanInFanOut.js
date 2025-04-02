import React from 'react';
import MetricsForm from '../components/MetricsForm';
import '../components/css/FanInFanOut.css';

const FanInFanOut = () => {
  return (
    <div className="fan-metrics-container">
      {/* <h2 className="metrics-title">Fan-In / Fan-Out Metrics</h2> */}
      <MetricsForm />
    </div>
  );
};

export default FanInFanOut;
