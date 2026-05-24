import { Link } from 'react-router-dom'

function DatasetPage() {
  return (
    <div className="container dashboard-shell">
      <header className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Dataset center</h1>
        </div>
        <Link to="/" className="button button-secondary">Back to dashboard</Link>
      </header>
      <section className="card">
        <h2>Registered datasets</h2>
        <p>This view is reserved for detailed dataset drill-downs, quality summaries, and per-record operations.</p>
      </section>
    </div>
  )
}

export default DatasetPage
