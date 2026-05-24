import { Link } from 'react-router-dom'

function ArtifactPage() {
  return (
    <div className="container dashboard-shell">
      <header className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Artifact center</h1>
        </div>
        <Link to="/" className="button button-secondary">Back to dashboard</Link>
      </header>
      <section className="card">
        <h2>Artifact registry</h2>
        <p>Download generated reports, logs, and model-ready datasets from this area.</p>
      </section>
    </div>
  )
}

export default ArtifactPage
