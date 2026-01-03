import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from "./components/Sidebar";
import App from "./pages/Home/App";
import Downloads from "./pages/downloads/Downloads";
import Sources from "./pages/sources/Sources";
import Logs from "./pages/Logs";
import './pages/Home/App.css';

function Layout() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/downloads" element={<Downloads />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default Layout;