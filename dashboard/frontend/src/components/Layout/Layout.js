
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiBarChart2, FiCalendar, FiTrendingUp, FiMap, FiSettings, FiMenu, FiX } from 'react-icons/fi';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <FiBarChart2 /> },
    { path: '/events', label: 'Event Analysis', icon: <FiCalendar /> },
    { path: '/changepoint', label: 'Change Points', icon: <FiTrendingUp /> },
    { path: '/correlation', label: 'Correlations', icon: <FiMap /> },
    { path: '/insights', label: 'Insights', icon: <FiSettings /> },
  ];

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="container-fluid">
          <div className="header-content">
            <div className="header-left">
              <button 
                className="sidebar-toggle"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
              </button>
              <div className="header-title">
                <h1>Brent Oil Analysis</h1>
                <p className="header-subtitle">Bayesian Change Point Detection Dashboard</p>
              </div>
            </div>
            <div className="header-right">
              <div className="status-indicator">
                <span className="status-dot active"></span>
                <span>API Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="app-main">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav className="sidebar-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            ))}
          </nav>
          
          <div className="sidebar-footer">
            <div className="data-info">
              <div className="info-item">
                <span className="info-label">Data Range:</span>
                <span className="info-value">1987-2020</span>
              </div>
              <div className="info-item">
                <span className="info-label">Events:</span>
                <span className="info-value">24</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
          <div className="container-fluid">
            {children}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container-fluid">
          <div className="footer-content">
            <div className="footer-left">
              <p>Birhan Energies • Oil Market Intelligence</p>
            </div>
            <div className="footer-right">
              <p>© {new Date().getFullYear()} • Bayesian Analysis Dashboard</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;