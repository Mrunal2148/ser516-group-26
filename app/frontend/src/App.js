import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Footer from "./components/Footer";
import MainContent from "./components/MainContent";
import "./App.css"; 

const App = () => {
  return (
    <Router>
      <div className="app">
        <Header />
        <div className="content">
          <Sidebar />
          <MainContent /> {/* This component will now handle routing */}
        </div>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
