import React from 'react';
import MetricsForm from '../components/MetricsForm';
import '../components/css/FanInFanOut.css';
import FanInFanOutCalculator from '../components/FanInFanOutCalculator';

/*const FanInFanOut = () => {
  return (
    <div className="fan-metrics-container">
      {/* <h2 className="metrics-title">Fan-In / Fan-Out Metrics</h2> *'/}
      <MetricsForm />
    </div>
  );
};
*/

const FanInFanOut = () => {
  return (
    <div className="fan-metrics-container">
      {<h2 className="metrics-title">Fan-In / Fan-Out Metrics</h2>}
      <FanInFanOutCalculator />
    </div>
  );
};

export default FanInFanOut;
