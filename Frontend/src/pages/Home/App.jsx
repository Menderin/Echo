import { useState, useEffect } from 'react'
import {
    MdRadio,
    MdBarChart,
    MdToday,
    MdPlayArrow,
    MdRefresh,
    MdDelete,
    MdHistory
} from 'react-icons/md'
import {
    FiRefreshCw,
    FiTrash2,
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
    const [loading, setLoading] = useState(false)
    const [episodes, setEpisodes] = useState([])

    // Cargar episodios al iniciar
    useEffect(() => {
        fetchEpisodes()
    }, [])

    const fetchEpisodes = async () => {
        setLoading(true)
        try {
            // 1. Primero sincronizar archivos del disco con la base de datos
            console.log("Sincronizando archivos del disco...")
            const syncResponse = await fetch('http://localhost:8000/sync', {
                method: 'POST'
            })

            if (syncResponse.ok) {
                const syncData = await syncResponse.json()
                console.log(`Sincronización completada: ${syncData.added} archivos nuevos`)

                // Si hubo errores, mostrarlos en consola
                if (syncData.errors && syncData.errors.length > 0) {
                    console.warn("Errores durante sincronización:", syncData.errors)
                }
            } else {
                console.error("Error al sincronizar archivos")
            }

            // 2. Luego obtener la lista actualizada de episodios
            console.log("Obteniendo lista de episodios...")
            const response = await fetch('http://localhost:8000/episodes')
            if (response.ok) {
                const data = await response.json()
                setEpisodes(data)
                console.log(`${data.length} episodios cargados`)
            }
        } catch (error) {
            console.error("Error fetching episodes:", error)
            setStatus({
                type: 'error',
                message: `Error al actualizar: ${error.message}`
            })
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
            return source === 'youtube';
        }).length,
        stream: episodes.filter(ep => {
            const source = ep.source?.toLowerCase();
            return source === 'stream';
        }).length
    }

    // Helper para formatear el source de forma user-friendly
    const formatSource = (source) => {
        const sourceMap = {
            'youtube': 'YouTube',
            'stream': 'Transmisión en Vivo',
            'local': 'Archivo Local',
            'local_scan': 'Archivo Local'
        };
        return sourceMap[source] || source || 'Desconocido';
    };



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
                            <FiRefreshCw className={`btn-icon ${loading ? 'spinning' : ''}`} />
                            {loading ? 'Sincronizando...' : 'Actualizar'}
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
                                {episodes.map((ep) => (
                                    <tr key={ep.id}>
                                        <td>
                                            <span className="program-title">
                                                {ep.title || 'Sin título'}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="source-badge">
                                                {formatSource(ep.source)}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="date-cell">
                                                {new Date(ep.created_at).toLocaleDateString()} {new Date(ep.created_at).toLocaleTimeString([], {
                                                    hour: '2-digit',
                                                    minute: '2-digit'
                                                })}
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
                    </div>
                )}
            </div>
        </div>
    )
}

export default App
