import React, { useEffect, useState, useRef } from 'react';
import './Logs.css';

function Logs() {
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [levelFilter, setLevelFilter] = useState('');
  const [qFilter, setQFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggTimer = useRef(null);

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip, levelFilter]);

  async function fetchLogs() {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.set('skip', skip.toString());
      params.set('limit', limit.toString());
      if (levelFilter) params.set('level', levelFilter);
      if (qFilter) params.set('q', qFilter);

      const res = await fetch(`${API_BASE}/logs?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      setLogs(body.items || []);
      setTotal(body.total || 0);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  // Debounced suggestions when typing in the search box
  useEffect(() => {
    if (suggTimer.current) clearTimeout(suggTimer.current);
    if (!qFilter || qFilter.length < 2) {
      setSuggestions([]);
      return;
    }

    suggTimer.current = setTimeout(async () => {
      try {
        const params = new URLSearchParams();
        params.set('q', qFilter);
        params.set('limit', '6');
        const res = await fetch(`${API_BASE}/logs?${params.toString()}`);
        if (!res.ok) return;
        const body = await res.json();
        const uniq = [];
        (body.items || []).forEach((it) => {
          const txt = (it.message || it.source || '').trim();
          if (txt && !uniq.includes(txt)) uniq.push(txt);
        });
        setSuggestions(uniq.slice(0, 6));
        setShowSuggestions(true);
      } catch (e) {
        // ignore suggestion errors
      }
    }, 300);

    return () => {
      if (suggTimer.current) clearTimeout(suggTimer.current);
    };
  }, [qFilter]);

  function onSearch(e) {
    e?.preventDefault();
    setSkip(0);
    fetchLogs();
  }

  function prevPage() {
    setSkip(Math.max(0, skip - limit));
  }

  function nextPage() {
    if (skip + limit < total) setSkip(skip + limit);
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">📋 Logs / Historial</h1>
        <p className="page-subtitle">Registro de actividades y errores del sistema</p>
      </div>

      <div className="card">
        <h2 className="card-title">Historial de eventos</h2>

        <form className="logs-filters" onSubmit={onSearch}>
          <div className="filter-row">
            <label>Nivel:</label>
            <select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)}>
              <option value="">Todos</option>
              <option value="INFO">INFO</option>
              <option value="WARN">WARN</option>
              <option value="ERROR">ERROR</option>
            </select>
            <label>Búsqueda:</label>
            <div className="search-wrapper">
              <input
                type="search"
                placeholder="texto o mensaje"
                value={qFilter}
                onChange={(e) => setQFilter(e.target.value)}
                onFocus={() => { if (suggestions.length) setShowSuggestions(true); }}
              />
              {showSuggestions && suggestions.length > 0 && (
                <ul className="suggestions-list">
                  {suggestions.map((s, i) => (
                    <li
                      key={i}
                      onMouseDown={(ev) => {
                        ev.preventDefault();
                        setQFilter(s);
                        setShowSuggestions(false);
                        setSkip(0);
                        fetchLogs();
                      }}
                    >
                      {s}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <button className="btn" type="submit">Buscar</button>
          </div>
        </form>

        {loading && <div className="logs-loading">Cargando...</div>}
        {error && <div className="logs-error">Error: {error}</div>}

        <div className="logs-table">
          <div className="logs-header">
            <div>Fecha</div>
            <div>Nivel</div>
            <div>Mensaje</div>
            <div>Fuente</div>
            <div>Acciones</div>
            <div></div>
          </div>
          {logs.length === 0 && !loading && <div className="logs-empty">No hay registros.</div>}
          {logs.map((l) => (
            <div className="logs-row" key={l.id}>
              <div className="log-cell">{new Date(l.timestamp).toLocaleString()}</div>
              <div className="log-cell"><span className={`badge badge-${l.level?.toLowerCase()}`}>{l.level}</span></div>
              <div className="log-cell log-message">{l.message}</div>
              <div className="log-cell">{l.source}</div>
              <div className="log-cell"><button className="btn small" onClick={() => setSelected(l)}>Detalles</button></div>
            </div>
          ))}
        </div>

        <div className="logs-footer">
          <div>Total: {total}</div>
          <div className="pagination">
            <button className="btn" onClick={prevPage} disabled={skip === 0}>Anterior</button>
            <button className="btn" onClick={nextPage} disabled={skip + limit >= total}>Siguiente</button>
          </div>
        </div>
      </div>

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{selected.level} — {new Date(selected.timestamp).toLocaleString()}</h3>
            <p><strong>Mensaje:</strong> {selected.message}</p>
            {selected.details && (
              <div className="modal-details">
                <strong>Detalles:</strong>
                <pre>{selected.details}</pre>
              </div>
            )}
            <div className="modal-actions">
              <button className="btn" onClick={() => setSelected(null)}>Cerrar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Logs;