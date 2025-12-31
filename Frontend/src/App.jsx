import { useState, useEffect } from 'react'
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
                setStatus({ type: 'success', message: `Resultado: ${data.status}` })
                fetchEpisodes() // Recargar la lista
            } else {
                setStatus({ type: 'error', message: `Error: ${data.detail || 'Error desconocido'}` })
            }
        } catch (error) {
            setStatus({ type: 'error', message: `Error de conexión: ${error.message}` })
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
                fetchEpisodes() // Recargar la lista
            } else {
                alert("Error al eliminar")
            }
        } catch (error) {
            console.error("Error deleting episode:", error)
        }
    }

    const handleSync = async () => {
        setLoading(true)
        try {
            const response = await fetch('http://localhost:8000/sync', {
                method: 'POST'
            })
            const data = await response.json()
            if (response.ok) {
                alert(data.message)
                fetchEpisodes()
            } else {
                alert("Error al sincronizar")
            }
        } catch (error) {
            console.error("Error syncing:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleCleanup = async () => {
        if (!confirm("¿Eliminar registros de archivos que ya no existen?")) return

        setLoading(true)
        try {
            const response = await fetch('http://localhost:8000/cleanup', {
                method: 'POST'
            })
            const data = await response.json()
            if (response.ok) {
                alert(data.message)
                fetchEpisodes()
            } else {
                alert("Error al limpiar")
            }
        } catch (error) {
            console.error("Error cleaning up:", error)
        } finally {
            setLoading(false)
        }
    }


    return (
        <div className="container">
            <h1>📻 Radio Autonoma Downloader</h1>

            <form onSubmit={handleSubmit} className="download-form">
                <div className="form-group">
                    <label>ID del Programa:</label>
                    <input
                        type="text"
                        name="id"
                        value={formData.id}
                        onChange={handleChange}
                        placeholder="Ej: noticias_mañana"
                        required
                    />
                </div>

                <div className="form-group">
                    <label>URL:</label>
                    <input
                        type="url"
                        name="url"
                        value={formData.url}
                        onChange={handleChange}
                        placeholder="https://..."
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Fuente:</label>
                    <select name="source" value={formData.source} onChange={handleChange}>
                        <option value="youtube">YouTube</option>
                        <option value="stream">Radio Stream</option>
                    </select>
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? 'Descargando...' : 'Iniciar Descarga'}
                </button>
            </form>

            {status && (
                <div className={`status-message ${status.type}`}>
                    {status.message}
                </div>
            )}

            <div className="episodes-list">
                <div className="list-header">
                    <h2>📚 Episodios Descargados</h2>
                    <div className="header-buttons">
                        <button onClick={handleSync} disabled={loading} className="sync-btn">
                            🔄 Sincronizar
                        </button>
                        <button onClick={handleCleanup} disabled={loading} className="cleanup-btn">
                            🧹 Limpiar
                        </button>
                    </div>
                </div>

                {episodes.length === 0 ? (
                    <p>No hay descargas aún.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Fuente</th>
                                <th>Fecha</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {episodes.map((ep) => (
                                <tr key={ep.id}>
                                    <td>{ep.title}</td>
                                    <td>{ep.station_name}</td>
                                    <td>{new Date(ep.created_at).toLocaleString()}</td>
                                    <td>
                                        <button
                                            className="delete-btn"
                                            onClick={() => handleDelete(ep.id)}
                                        >
                                            🗑️
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default App
