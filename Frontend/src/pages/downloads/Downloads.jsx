import { useState } from 'react';
import {
  MdDownload,
  MdCloudUpload
} from 'react-icons/md';
import {
  FiRefreshCw,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import './Downloads.css';

function Downloads() {
  const [formData, setFormData] = useState({
    id: '',
    url: '',
    source: 'youtube'
  });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch('http://localhost:8000/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus({ type: 'success', message: `Descarga Completada: ${data.status}` });
        // Limpiar formulario después de descarga exitosa
        setFormData({ id: '', url: '', source: 'youtube' });
      } else {
        setStatus({ type: 'error', message: `❌ Error: ${data.detail || 'Error desconocido'}` });
      }
    } catch (error) {
      setStatus({ type: 'error', message: `❌ Error de conexión: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="section-title-container">
          <MdDownload className="section-title-icon" />
          <h1 className="page-title">Descargas</h1>
        </div>
        <p className="page-subtitle">Gestión de descargas programadas y manuales</p>
      </div>

      {/* SECCIÓN DE DESCARGA MANUAL */}
      <div className="dashboard-section">
        <div className="section-header">
          <div className="section-title-container">
            <MdDownload className="section-title-icon" />
            <h2>Ejecutar tarea manual</h2>
          </div>
          <p>Descarga manual de programas</p>
        </div>

        <form onSubmit={handleSubmit} className="modern-form">
          <div className="form-row">
            <div className="form-group">
              <label>ID del Programa</label>
              <input
                type="text"
                name="id"
                value={formData.id}
                onChange={handleChange}
                placeholder="Ej: noticias_matinal"
                required
              />
            </div>

            <div className="form-group">
              <label>Fuente</label>
              <select
                name="source"
                value={formData.source}
                onChange={handleChange}
              >
                <option value="youtube">YouTube</option>
                <option value="stream">Radio Stream (HTTP)</option>
                <option value="elsitiocristiano">El Sitio Cristiano</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>URL</label>
            <input
              type="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              placeholder="https://www.youtube.com/watch?v=..."
              required
            />
          </div>

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? (
              <>
                <FiRefreshCw className="btn-icon spinning" />
                Descargando...
              </>
            ) : (
              <>
                <MdCloudUpload className="btn-icon" />
                Iniciar Descarga
              </>
            )}
          </button>
        </form>

        {status && (
          <div className={`status-alert ${status.type}`}>
            {status.type === 'success' ? (
              <FiCheckCircle className="alert-icon" />
            ) : (
              <FiAlertCircle className="alert-icon" />
            )}
            {status.message}
          </div>
        )}
      </div>
    </div>
  );
}

export default Downloads;