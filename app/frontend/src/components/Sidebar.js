import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaTachometerAlt, FaCog, FaCalculator } from 'react-icons/fa';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <ul>
        <li className="sidebar-item">
          <NavLink to="/">
            <FaHome />
            <span className="icon-text">Home</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/AddProject">
            <FaTachometerAlt />
            <span className="icon-text">Add Projects</span>
          </NavLink>
        </li>
        <li className="sidebar-item">
          <NavLink to="/runmetric">
            <FaCalculator />
            <span className="icon-text">Run Metrics</span>
          </NavLink>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
