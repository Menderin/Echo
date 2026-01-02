import { useState, useEffect } from 'react'
import { 
  MdRadio, 
  MdBarChart, 
  MdToday, 
  MdPlayArrow,
  MdDownload,
  MdRefresh,
  MdDelete,
  MdCloudUpload,
  MdHistory
} from 'react-icons/md'
import { 
  FiRefreshCw,
  FiTrash2,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi'
import { 
  BsYoutube, 
  BsBroadcast,
  BsCalendar,
  BsCollection
} from 'react-icons/bs'
import './App.css'

function App() {
    const [formData, setFormData] = useState({
        id: '',
        url: '',
        source: 'youtube'
    })
    const [status, setStatus] = useState(null)
    const [loading, setLoading] = useState(false)
    const [episodes, setEpisodes] = useState([])

    // Cargar episodios al iniciar
    useEffect(() => {
        fetchEpisodes()
    }, [])

    const fetchEpisodes = async () => {
        try {
            const response = await fetch('http://localhost:8000/episodes')
            if (response.ok) {
                const data = await response.json()
                setEpisodes(data)
            }
        } catch (error) {
            console.error("Error fetching episodes:", error)
        }
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setStatus(null)

        try {
            const response = await fetch('http://localhost:8000/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })

            const data = await response.json()

            if (response.ok) {
                setStatus({ type: 'success', message: `Descarga Completada: ${data.status}` })
                fetchEpisodes()
            } else {
                setStatus({ type: 'error', message: `❌ Error: ${data.detail || 'Error desconocido'}` })
            }
        } catch (error) {
            setStatus({ type: 'error', message: `❌ Error de conexión: ${error.message}` })
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id) => {
        if (!confirm("¿Estás seguro de eliminar este episodio?")) return

        try {
            const response = await fetch(`http://localhost:8000/episodes/${id}`, {
                method: 'DELETE'
            })

            if (response.ok) {
                fetchEpisodes()
            } else {
                alert("Error al eliminar")
            }
        } catch (error) {
            console.error("Error deleting episode:", error)
        }
    }

    // Estadísticas para el dashboard
    const stats = {
        total: episodes.length,
        today: episodes.filter(ep => {
            const today = new Date()
            const epDate = new Date(ep.created_at)
            return epDate.toDateString() === today.toDateString()
        }).length,
        youtube: episodes.filter(ep => {
            const source = ep.source?.toLowerCase();
            const station = ep.station_name?.toLowerCase();
            return source === 'youtube' || 
                station === 'youtube' || 
                station?.includes('youtube') ||
                ep.title?.toLowerCase().includes('youtube');
        }).length,
        stream: episodes.filter(ep => {
            const source = ep.source?.toLowerCase();
            const station = ep.station_name?.toLowerCase();
            return source === 'stream' || 
                station === 'stream' || 
                station?.includes('stream');
        }).length
    }

    return (
        <div className="dashboard">

            {/* ================= HEADER DEL DASHBOARD ================= */}
            <div className="dashboard-header">
                <div className="dashboard-header-left">
                    <div className="dashboard-title-container">
                        <MdRadio className="dashboard-title-icon" />
                        <h1 className="dashboard-title">Echo Radio</h1>
                    </div>
                    <span className="dashboard-status">
                        <span className="status-dot active">
                            <FiCheckCircle size={10} />
                        </span>
                        Sistema activo · America/Santiago
                    </span>
                </div>

                <button
                    className="primary-btn small"
                    onClick={() => alert('Ejecución manual global (pendiente)')}
                >
                    <MdPlayArrow className="btn-icon" />
                    Ejecutar tarea manual
                </button>
            </div>
            {/* ======================================================== */}

            {/* CARDS DE ESTADÍSTICAS */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">
                        <MdBarChart size={24} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total}</div>
                        <div className="stat-label">Total Descargas</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <BsCalendar size={22} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.today}</div>
                        <div className="stat-label">Hoy</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <BsYoutube size={22} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.youtube}</div>
                        <div className="stat-label">YouTube</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">
                        <BsBroadcast size={22} />
                    </div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.stream}</div>
                        <div className="stat-label">Stream</div>
                    </div>
                </div>
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
                                <option value="stream">Radio Stream</option>
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

            {/* TABLA DE EPISODIOS */}
            <div className="dashboard-section">
                <div className="section-header">
                    <div className="section-title-container">
                        <BsCollection className="section-title-icon" />
                        <h2>Programas Recientes</h2>
                    </div>
                    <div className="section-actions">
                        <button
                            onClick={fetchEpisodes}
                            className="action-btn"
                            disabled={loading}
                        >
                            <FiRefreshCw className="btn-icon" />
                            Actualizar
                        </button>
                    </div>
                </div>

                {episodes.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">
                            <MdHistory size={48} />
                        </div>
                        <h3>No hay descargas aún</h3>
                        <p>Comienza descargando un programa usando el formulario arriba.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="modern-table">
                            <thead>
                                <tr>
                                    <th>Programa</th>
                                    <th>Fuente</th>
                                    <th>Fecha</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {episodes.slice(0, 5).map((ep) => (
                                    <tr key={ep.id}>
                                        <td>
                                            <span className="program-title">
                                                {ep.title || 'Sin título'}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="source-badge">
                                                {ep.station_name || ep.source}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="date-cell">
                                                <span className="date">
                                                    {new Date(ep.created_at).toLocaleDateString()}
                                                </span>
                                                <span className="time">
                                                    {new Date(ep.created_at).toLocaleTimeString([], {
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    })}
                                                </span>
                                            </div>
                                        </td>
                                        <td>
                                            <button
                                                className="icon-btn delete"
                                                onClick={() => handleDelete(ep.id)}
                                                title="Eliminar episodio"
                                            >
                                                <FiTrash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {episodes.length > 5 && (
                            <div className="table-footer">
                                <span>
                                    Mostrando 5 de {episodes.length} programas
                                </span>
                                <button className="text-btn">
                                    Ver todos →
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default App
