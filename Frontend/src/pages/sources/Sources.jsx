import { useState, useEffect } from 'react';
import {
    MdRadio,
    MdAdd,
    MdEdit,
    MdDelete,
    MdSave,
    MdCancel,
    MdAccessTime
} from 'react-icons/md';
import {
    FiRefreshCw,
    FiCheckCircle,
    FiAlertCircle
} from 'react-icons/fi';
import {
    BsYoutube,
    BsBroadcast
} from 'react-icons/bs';
import './Sources.css';

function Sources() {
    const [sources, setSources] = useState([]);
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        source_type: 'youtube',
        url: '',
        description: '',
        schedule_time: '',
        duration_minutes: 60,
        active: true
    });
    const [editingId, setEditingId] = useState(null);
    const [status, setStatus] = useState(null);

    // Cargar fuentes al iniciar
    useEffect(() => {
        fetchSources();
    }, []);

    const fetchSources = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/sources');
            if (response.ok) {
                const data = await response.json();
                setSources(data);
            }
        } catch (error) {
            console.error("Error fetching sources:", error);
            setStatus({ type: 'error', message: `Error al cargar fuentes: ${error.message}` });
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus(null);

        try {
            const url = editingId
                ? `http://localhost:8000/sources/${editingId}`
                : 'http://localhost:8000/sources';

            const method = editingId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                setStatus({
                    type: 'success',
                    message: editingId ? 'Fuente actualizada exitosamente' : 'Fuente creada exitosamente'
                });
                resetForm();
                fetchSources();
            } else {
                const error = await response.json();
                setStatus({ type: 'error', message: `Error: ${error.detail}` });
            }
        } catch (error) {
            setStatus({ type: 'error', message: `Error de conexión: ${error.message}` });
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (source) => {
        setFormData({
            name: source.name,
            source_type: source.source_type,
            url: source.url,
            description: source.description || '',
            schedule_time: source.schedule_time || '',
            duration_minutes: source.duration_minutes || 60,
            active: source.active
        });
        setEditingId(source.id);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleDelete = async (id) => {
        if (!confirm("¿Estás seguro de eliminar esta fuente?")) return;

        try {
            const response = await fetch(`http://localhost:8000/sources/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                setStatus({ type: 'success', message: 'Fuente eliminada exitosamente' });
                fetchSources();
            }
        } catch (error) {
            console.error("Error deleting source:", error);
            setStatus({ type: 'error', message: 'Error al eliminar fuente' });
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            source_type: 'youtube',
            url: '',
            description: '',
            schedule_time: '',
            duration_minutes: 60,
            active: true
        });
        setEditingId(null);
    };

    const getSourceIcon = (type) => {
        if (type === 'youtube') return <BsYoutube />;
        if (type === 'elsitiocristiano') return <MdRadio />;
        return <BsBroadcast />;
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <div className="section-title-container">
                    <MdRadio className="section-title-icon" />
                    <h1 className="page-title">Gestión de Fuentes</h1>
                </div>
                <p className="page-subtitle">Administra las fuentes de contenido para descargas automáticas</p>
            </div>

            {/* FORMULARIO DE FUENTE */}
            <div className="dashboard-section">
                <div className="section-header">
                    <div className="section-title-container">
                        <MdAdd className="section-title-icon" />
                        <h2>{editingId ? 'Editar Fuente' : 'Agregar Nueva Fuente'}</h2>
                    </div>
                    {editingId && (
                        <button onClick={resetForm} className="action-btn">
                            <MdCancel className="btn-icon" />
                            Cancelar
                        </button>
                    )}
                </div>

                <form onSubmit={handleSubmit} className="modern-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label>Nombre del Programa *</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Ej: Radio Japón"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Tipo de Fuente *</label>
                            <select
                                name="source_type"
                                value={formData.source_type}
                                onChange={handleChange}
                            >
                                <option value="youtube">YouTube</option>
                                <option value="stream">Radio Stream (HTTP)</option>
                                <option value="elsitiocristiano">El Sitio Cristiano</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>URL *</label>
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
                        <label>Descripción</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Descripción del programa..."
                            rows="3"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Horario de Emisión</label>
                            <input
                                type="time"
                                name="schedule_time"
                                value={formData.schedule_time}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Duración (minutos)</label>
                            <input
                                type="number"
                                name="duration_minutes"
                                value={formData.duration_minutes}
                                onChange={handleChange}
                                min="1"
                                placeholder="60"
                            />
                        </div>
                    </div>

                    <div className="form-group-checkbox">
                        <label>
                            <input
                                type="checkbox"
                                name="active"
                                checked={formData.active}
                                onChange={handleChange}
                            />
                            <span>Fuente activa</span>
                        </label>
                    </div>

                    <button type="submit" className="primary-btn" disabled={loading}>
                        {loading ? (
                            <>
                                <FiRefreshCw className="btn-icon spinning" />
                                {editingId ? 'Actualizando...' : 'Guardando...'}
                            </>
                        ) : (
                            <>
                                <MdSave className="btn-icon" />
                                {editingId ? 'Actualizar Fuente' : 'Guardar Fuente'}
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

            {/* LISTA DE FUENTES */}
            <div className="dashboard-section">
                <div className="section-header">
                    <div className="section-title-container">
                        <MdRadio className="section-title-icon" />
                        <h2>Fuentes Registradas ({sources.length})</h2>
                    </div>
                    <button
                        onClick={fetchSources}
                        className="action-btn"
                        disabled={loading}
                    >
                        <FiRefreshCw className={`btn-icon ${loading ? 'spinning' : ''}`} />
                        Actualizar
                    </button>
                </div>

                {sources.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">
                            <MdRadio size={48} />
                        </div>
                        <h3>No hay fuentes registradas</h3>
                        <p>Agrega tu primera fuente de contenido usando el formulario arriba.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="modern-table">
                            <thead>
                                <tr>
                                    <th>Programa</th>
                                    <th>Tipo</th>
                                    <th>Horario</th>
                                    <th>Duración</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sources.map((source) => (
                                    <tr key={source.id}>
                                        <td>
                                            <div className="source-name">
                                                {getSourceIcon(source.source_type)}
                                                <div>
                                                    <strong>{source.name}</strong>
                                                    {source.description && (
                                                        <p className="source-desc">{source.description}</p>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className="source-badge">
                                                {source.source_type === 'youtube' && 'YouTube'}
                                                {source.source_type === 'stream' && 'Stream HTTP'}
                                                {source.source_type === 'elsitiocristiano' && 'El Sitio Cristiano'}
                                            </span>
                                        </td>
                                        <td>
                                            {source.schedule_time ? (
                                                <span className="time-badge">
                                                    <MdAccessTime size={14} />
                                                    {source.schedule_time}
                                                </span>
                                            ) : (
                                                <span className="text-muted">-</span>
                                            )}
                                        </td>
                                        <td>{source.duration_minutes} min</td>
                                        <td>
                                            <span className={`status-badge ${source.active ? 'active' : 'inactive'}`}>
                                                {source.active ? 'Activa' : 'Inactiva'}
                                            </span>
                                        </td>
                                        <td>
                                            <div className="action-buttons">
                                                <button
                                                    className="icon-btn edit"
                                                    onClick={() => handleEdit(source)}
                                                    title="Editar fuente"
                                                >
                                                    <MdEdit size={16} />
                                                </button>
                                                <button
                                                    className="icon-btn delete"
                                                    onClick={() => handleDelete(source.id)}
                                                    title="Eliminar fuente"
                                                >
                                                    <MdDelete size={16} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Sources;
