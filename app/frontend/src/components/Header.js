import React, { useState, useEffect } from 'react';
import asuLogo from '../components/css/ASU-logo.png'; 

const Header = () => {
  const [version, setVersion] = useState("");

  useEffect(() => {
    fetch('/version.txt') 
      .then(response => response.text())
      .then(data => setVersion(data.trim())) 
      .catch(error => console.error("Error loading version:", error));
  }, []);

  return (
    <header className="header" style={{ 
      display: "flex", 
      alignItems: "center", 
      justifyContent: "space-between", 
      padding: "5px 20px", 
      borderBottom: "2px solid #ccc"
    }}>

      <img src={asuLogo} alt="ASU Logo" style={{ height: "70px", width: "auto" }} />


      <h1 style={{ margin: 0,padding: "5px 0px", textAlign: "center", flex: 1 }}>Project Metrics Calculator</h1>


      {version && (
        <p style={{ fontSize: "14px", fontWeight: "bold", margin: 0 }}>
          Version: {version}
        </p>
      )}
    </header>
  );
};

export default Header;
