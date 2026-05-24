function ExecutionConsole({ logs = [] }) {
  return (
    <section className="execution-console card">
      <div className="execution-console__header">
        <div>
          <p className="eyebrow">Telemetry</p>
          <h3>Execution console</h3>
        </div>
        <span>{logs.length} events</span>
      </div>
      <div className="execution-log-list">
        {logs.length === 0 ? (
          <p className="execution-empty">No live events yet.</p>
        ) : (
          logs.map((entry, index) => (
            <div key={`${entry.stage || entry.message}-${index}`} className={`execution-log execution-log--${entry.status || 'success'}`}>
              <div className="execution-log__meta">
                <strong>{entry.stage || entry.source || 'System'}</strong>
                <span>{entry.duration ? `${entry.duration}s` : entry.timestamp || 'now'}</span>
              </div>
              <p>{entry.message || entry.error || entry.status}</p>
            </div>
          ))
        )}
      </div>
    </section>
  )
}

export default ExecutionConsole
