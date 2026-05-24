import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home-container">
      <header className="navbar navbar--home">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Dataset preparation, engineered for production</h1>
        </div>
        <div className="nav-actions">
          <Link to="/upload" className="button button-primary">
            Open Workspace
          </Link>
          <a href="#capabilities" className="button button-secondary button-secondary--ghost">
            Explore Capabilities
          </a>
        </div>
      </header>

      <main className="container home-layout">
        <section className="hero card hero-card">
          <div className="hero-copy">
            <p className="eyebrow">Filesystem-backed pipeline</p>
            <h2>Analyze, clean, infer, and export datasets with a single workflow.</h2>
            <p>
              Upload CSV, Excel, or JSON files and move them through analysis, preprocessing,
              intelligence discovery, and export without a database dependency.
            </p>

            <div className="cta-buttons cta-buttons--left">
              <Link to="/upload" className="button button-primary">
                Start an upload
              </Link>
              <a href="#flow" className="button button-secondary button-secondary--ghost">
                See the flow
              </a>
            </div>
          </div>

          <div className="hero-metrics">
            <div className="metric-card">
              <span>Upload</span>
              <strong>Raw files</strong>
              <p>Direct to filesystem</p>
            </div>
            <div className="metric-card">
              <span>Analysis</span>
              <strong>Quality scores</strong>
              <p>Missing data and duplicates</p>
            </div>
            <div className="metric-card">
              <span>Intelligence</span>
              <strong>Patterns</strong>
              <p>Correlations and cardinality</p>
            </div>
          </div>
        </section>

        <section id="flow" className="content-section">
          <div className="section-heading">
            <p className="eyebrow">Pipeline</p>
            <h3>Structured processing from ingestion to export</h3>
          </div>

          <div className="workflow-grid">
            <div className="workflow-card">
              <span>01</span>
              <h4>Upload</h4>
              <p>Store files and metadata in the local filesystem.</p>
            </div>
            <div className="workflow-card">
              <span>02</span>
              <h4>Analyze</h4>
              <p>Measure completeness, duplicates, and basic quality.</p>
            </div>
            <div className="workflow-card">
              <span>03</span>
              <h4>Preprocess</h4>
              <p>Clean data, deduplicate rows, and write a cleaned CSV.</p>
            </div>
            <div className="workflow-card">
              <span>04</span>
              <h4>Intelligence</h4>
              <p>Discover correlations, cardinality, and data patterns.</p>
            </div>
            <div className="workflow-card">
              <span>05</span>
              <h4>Export</h4>
              <p>Deliver cleaned CSVs plus JSON reports and logs.</p>
            </div>
          </div>
        </section>

        <section id="capabilities" className="content-section">
          <div className="section-heading">
            <p className="eyebrow">Capabilities</p>
            <h3>Designed for professional dataset preparation</h3>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <h4>Multiple file types</h4>
              <p>CSV, XLSX, XLS, and JSON support with consistent schema extraction.</p>
            </article>
            <article className="feature-card">
              <h4>Filesystem architecture</h4>
              <p>Uploads, exports, and reports are stored on disk with predictable paths.</p>
            </article>
            <article className="feature-card">
              <h4>Quality reporting</h4>
              <p>Track missing cells, duplicates, and completeness from the same interface.</p>
            </article>
            <article className="feature-card">
              <h4>Pattern discovery</h4>
              <p>Generate intelligence reports with correlations, cardinality, and frequent values.</p>
            </article>
          </div>
        </section>
      </main>
    </div>
  )
}

export default Home
