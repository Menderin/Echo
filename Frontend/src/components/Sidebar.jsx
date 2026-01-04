import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

// Importar iconos profesionales de react-icons
import {
  MdDashboard,
  MdDownload,
  MdEdit,
  MdHistory,
  MdSettings,
  MdRadio,
  MdCheckCircle,
  MdRefresh
} from 'react-icons/md';
import {
  RiSignalTowerFill,
  RiCloudLine
} from 'react-icons/ri';
import {
  FiActivity
} from 'react-icons/fi';

const Sidebar = () => {
  const menuItems = [
    {
      path: '/',
      icon: <MdDashboard size={20} />,
      label: 'Home',
      description: 'Vista general'
    },
    {
      path: '/downloads',
      icon: <MdDownload size={20} />,
      label: 'Descargas',
      description: 'Descarga episodios'
    },
    {
      path: '/sources',
      icon: <RiSignalTowerFill size={20} />,
      label: 'Fuentes',
      description: 'Visualiza tus fuentes de descarga'
    },
    {
      path: '/editions',
      icon: <MdEdit size={20} />,
      label: 'Ediciones',
      description: 'Edita tus audios',
      badge: 'Próximo'
    },
    {
      path: '/logs',
      icon: <MdHistory size={20} />,
      label: 'Logs / Historial',
      description: 'Registro de actividades'
    },
    {
      path: '/settings',
      icon: <MdSettings size={20} />,
      label: 'Configuración',
      description: 'Ajustes del sistema'
    },
  ];

  const systemStats = {
    activeTasks: 2,
    lastSync: '15 min',
    storageUsed: '1.2 GB'
  };

  return (
    <div className="sidebar">
      {/* HEADER MEJORADO */}
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-icon">
            <MdRadio size={28} />
          </div>
          <div className="logo-text">
            <h2 className="sidebar-title">Echo Radio</h2>
            <p className="sidebar-subtitle">Automation System</p>
          </div>
        </div>
      </div>

      {/* NAVEGACIÓN MEJORADA */}
      <nav className="sidebar-nav">
        <div className="nav-section">
          <h3 className="nav-section-title">Navegación</h3>
          <ul className="nav-list">
            {menuItems.map((item) => (
              <li key={item.path} className="nav-item">
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'active' : ''}`
                  }
                >
                  <div className="nav-icon-wrapper">
                    {item.icon}
                  </div>
                  <div className="nav-content">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-description">{item.description}</span>
                  </div>
                  {item.badge && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* FOOTER MEJORADO */}
      <div className="sidebar-footer">
        <div className="connection-status">
          <div className="connection-info">
            <div className="status-indicator active">
              <MdCheckCircle size={12} />
            </div>
            <div className="connection-details">
              <span className="connection-label">Conectado</span>
              <span className="connection-server">localhost:8000</span>
            </div>
          </div>
          <div className="last-sync">
            <RiSignalTowerFill size={14} />
            <span>Sync: {systemStats.lastSync}</span>
          </div>
        </div>
        <div className="version-info">
          <span>v1.0.0 · Production</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;