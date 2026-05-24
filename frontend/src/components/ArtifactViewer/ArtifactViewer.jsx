function ArtifactViewer({ artifacts = [] }) {
  return (
    <section className="card">
      <div className="section-heading section-heading--compact">
        <p className="eyebrow">Artifacts</p>
        <h2>Output registry</h2>
      </div>
      <div className="artifact-grid">
        {artifacts.map((artifact) => (
          <a key={artifact.label} className="artifact-link" href={artifact.href} target="_blank" rel="noreferrer">
            {artifact.label}
          </a>
        ))}
      </div>
    </section>
  )
}

export default ArtifactViewer
