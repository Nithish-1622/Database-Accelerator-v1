function DatasetCard({ dataset, onRun, onOpenArtifacts }) {
  return (
    <article className="dataset-card--modern card">
      <div className="dataset-card__header">
        <div>
          <p className="eyebrow">Dataset</p>
          <h4>{dataset.name}</h4>
          <p>{dataset.description}</p>
        </div>
        <span className={`status-pill status-pill--${dataset.statusClass || 'ready'}`}>{dataset.status}</span>
      </div>
      <div className="dataset-info--grid">
        <div><span>Rows</span><strong>{dataset.rows}</strong></div>
        <div><span>Artifacts</span><strong>{dataset.artifacts}</strong></div>
      </div>
      <div className="action-grid">
        {onRun && <button className="button button-primary" onClick={() => onRun(dataset.id)}>Run</button>}
        {onOpenArtifacts && <button className="button button-secondary" onClick={() => onOpenArtifacts(dataset.id)}>Artifacts</button>}
      </div>
    </article>
  )
}

export default DatasetCard
