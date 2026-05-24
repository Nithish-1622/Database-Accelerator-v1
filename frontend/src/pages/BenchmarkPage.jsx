import { Link } from 'react-router-dom'

function BenchmarkPage() {
  return (
    <div className="container dashboard-shell">
      <header className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Benchmark center</h1>
        </div>
        <Link to="/" className="button button-secondary">Back to dashboard</Link>
      </header>
      <section className="card">
        <h2>Edge-case runs</h2>
        <p>Benchmark execution, stage timings, memory usage, and success-rate trends appear here.</p>
      </section>
    </div>
  )
}

export default BenchmarkPage
