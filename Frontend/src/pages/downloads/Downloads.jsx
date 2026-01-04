import { useState } from 'react';
import {
  MdDownload,
  MdCloudUpload,
  MdPlayArrow
} from 'react-icons/md';
import {
  FiRefreshCw,
  FiAlertCircle,
  FiCheckCircle,
  FiInfo
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
  const [bulkLoading, setBulkLoading] = useState(false);

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

  const handleDownloadAllSources = async () => {
    if (!confirm("¿Descargar el último episodio de TODAS las fuentes activas?")) return;

    setBulkLoading(true);
    setStatus(null);
    try {
      console.log("Iniciando descarga de todas las fuentes...");
      const response = await fetch('http://localhost:8000/download-all-sources', {
        method: 'POST'
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Resultado:", data);
        setStatus({
          type: 'success',
          message: `✅ Proceso completado: ${data.downloaded} descargados, ${data.skipped} saltados, ${data.errors.length} errores`
        });
      } else {
        const error = await response.json();
        setStatus({ type: 'error', message: `❌ Error: ${error.detail}` });
      }
    } catch (error) {
      console.error("Error al descargar fuentes:", error);
      setStatus({ type: 'error', message: '❌ Error al descargar fuentes' });
    } finally {
      setBulkLoading(false);
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

      {/* SECCIÓN DE DESCARGA AUTOMÁTICA */}
      <div className="dashboard-section">
        <div className="section-header">
          <div className="section-title-container">
            <MdPlayArrow className="section-title-icon" />
            <h2>Descarga Automática</h2>
          </div>
          <p>Descarga masiva de todas las fuentes configuradas</p>
        </div>

        {/* Info Box */}
        <div className="info-box">
          <div className="info-icon-wrapper">
            <FiInfo className="info-icon" />
          </div>
          <div className="info-content">
            <p>Descarga automáticamente el último episodio de <strong>todas las fuentes activas</strong> configuradas en el sistema.</p>
            <ul>
              <li><FiCheckCircle size={14} /> Verifica si el episodio ya existe antes de descargar</li>
              <li><FiCheckCircle size={14} /> Salta descargas duplicadas automáticamente</li>
              <li><FiCheckCircle size={14} /> Reporta errores individuales sin detener el proceso</li>
            </ul>
          </div>
        </div>

        {/* Botón de Descarga Masiva */}
        <button
          className="primary-btn large"
          onClick={handleDownloadAllSources}
          disabled={bulkLoading}
        >
          {bulkLoading ? (
            <>
              <FiRefreshCw className="btn-icon spinning" />
              Procesando...
            </>
          ) : (
            <>
              <MdPlayArrow className="btn-icon" />
              Descargar Todas las Fuentes
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default Downloads;