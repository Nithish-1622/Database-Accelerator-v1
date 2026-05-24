function BenchmarkCharts({ benchmarks = [] }) {
  return (
    <section className="card">
      <div className="section-heading section-heading--compact">
        <p className="eyebrow">Benchmarking</p>
        <h2>Execution snapshots</h2>
      </div>
      <div className="dashboard-summary__metrics">
        {benchmarks.map((metric) => (
          <article key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </article>
        ))}
      </div>
    </section>
  )
}

export default BenchmarkCharts
