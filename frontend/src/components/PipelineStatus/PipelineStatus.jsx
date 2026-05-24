function PipelineStatus({ stages = [] }) {
  return (
    <section className="card">
      <div className="section-heading section-heading--compact">
        <p className="eyebrow">Pipeline</p>
        <h2>Status</h2>
      </div>
      <div className="stage-list">
        {stages.map((stage, index) => (
          <div key={stage.label} className="stage-item">
            <span>{String(index + 1).padStart(2, '0')}</span>
            <p>{stage.label}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default PipelineStatus
