import React from 'react';
import './css/Dropdown.css';

const SelectDropdown = ({ label, options, selectedValue, onSelect }) => {
  return (
    <div className="input-group">
      <label htmlFor={label.replace(/\s+/g, '-').toLowerCase()}>{label}:</label>
      <select
        id={label.replace(/\s+/g, '-').toLowerCase()}
        value={selectedValue}
        onChange={(e) => onSelect(e.target.value)}
        className="dropdown-select"
      >
        <option value="">--Select--</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SelectDropdown;
