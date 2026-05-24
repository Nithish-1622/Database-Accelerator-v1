function KPISection({ metrics = [] }) {
  return (
    <section className="kpi-section card">
      <div className="section-heading section-heading--compact">
        <p className="eyebrow">Operations</p>
        <h2>Dashboard metrics</h2>
      </div>
      <div className="dashboard-summary__metrics">
        {metrics.map((metric) => (
          <article key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </article>
        ))}
      </div>
    </section>
  )
}

export default KPISection
