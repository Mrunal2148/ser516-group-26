import React from "react";
import mrunalImage from "./css/mrunal.jpeg";
import shreyaImage from "./css/Shreya.jpg";
import kmdImage from "./css/kmd.jpg";
import parthImage from "./css/ParthPatel.jpg"
const teamMembers = [
    {
        name: "Kaumudi Gulbarga",
        role: "Developer",
        image: kmdImage,
        description: "Student and Software Engineer.",
      },
    
    {
    name: "Mrunal Kapure",
    role: "Developer",
    image: mrunalImage,
    description: "Software engineer passionate about AI and automation.",
  },
  
  {
    name: "Parth Patel",
    role: "Developer",
    image: parthImage,
    description: "Software engineer passionate about AI and automation.",
  },
  {
    name: "Shreya Prakash",
    role: "Developer",
    image: shreyaImage,
    description: "A detail oriented programmer who turns coffee into code",
  }
];

const Home = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Welcome to the Project Metrics Calculator</h1>
      <p style={styles.description}>
        Our tool helps developers analyze and improve their code quality. It supports:
      </p>

      <div style={styles.metricsContainer}>
        <div style={styles.metricCard}>
          <h3>📖 Fog Index Metric</h3>
          <p>Measures readability of code comments to ensure clarity.</p>
        </div>
        <div style={styles.metricCard}>
          <h3>🛠️ Defects Removed Metric</h3>
          <p>Evaluates how many defects have been fixed from the codebase.</p>
        </div>
        <div style={styles.metricCard}>
          <h3>💬 Code Comment Coverage</h3>
          <p>Checks the percentage of commented code for maintainability.</p>
        </div>
      </div>

      <h2 style={styles.sectionTitle}>Meet Our Team</h2>
      <div style={styles.teamContainer}>
        {teamMembers.map((member, index) => (
          <div key={index} style={styles.teamCard}>
            <img src={member.image} alt={member.name} style={styles.teamImage} />
            <h3>{member.name}</h3>
            <p><strong>{member.role}</strong></p>
            <p>{member.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: "40px",
    textAlign: "center",
  },
  title: {
    fontSize: "28px",
    fontWeight: "bold",
    marginBottom: "15px",
  },
  description: {
    fontSize: "18px",
    color: "#555",
    marginBottom: "30px",
  },
  metricsContainer: {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
    flexWrap: "wrap",
  },
  metricCard: {
    width: "250px",
    padding: "20px",
    background: "white",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    textAlign: "center",
  },
  sectionTitle: {
    marginTop: "40px",
    fontSize: "24px",
    fontWeight: "bold",
  },
  teamContainer: {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
    flexWrap: "wrap",
    marginTop: "20px",
  },
  teamCard: {
    width: "200px",
    padding: "15px",
    background: "white",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    textAlign: "center",
  },
  teamImage: {
    width: "100px",
    height: "100px",
    borderRadius: "50%",
    marginBottom: "10px",
  },
};

export default Home;
