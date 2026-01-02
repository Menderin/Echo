import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from "./components/Sidebar"; 
import App from "./App";                  
import Downloads from "./pages/Downloads"; 
import Logs from "./pages/Logs";          
import './App.css';

function Layout() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/downloads" element={<Downloads />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default Layout;