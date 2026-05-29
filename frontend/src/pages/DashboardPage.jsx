import { Link } from 'react-router-dom'
import KPISection from '../components/KPISection/KPISection'
import ExecutionConsole from '../components/ExecutionConsole/ExecutionConsole'
import DatasetCard from '../components/DatasetCard/DatasetCard'
import ArtifactViewer from '../components/ArtifactViewer/ArtifactViewer'
import PipelineStatus from '../components/PipelineStatus/PipelineStatus'
import BenchmarkCharts from '../components/BenchmarkCharts/BenchmarkCharts'
import './DashboardPage.css'

const metrics = [
  { label: 'Active pipelines', value: '07' },
  { label: 'Published datasets', value: '128' },
  { label: 'Catalog artifacts', value: '564' },
  { label: 'Benchmark score', value: '98.4%' },
]

const stages = [
  { label: 'Source intake' },
  { label: 'Schema harmonization' },
  { label: 'Quality scoring' },
  { label: 'Feature assembly' },
  { label: 'Publishing' },
]

const datasets = [
  { id: 'ds-01', name: 'Customer churn refresh', description: 'Nightly object-store to lakehouse sync', rows: '120K', artifacts: '6', status: 'Ready', statusClass: 'ready' },
  { id: 'ds-02', name: 'Product telemetry', description: 'Streaming events with catalog publishing', rows: '45K', artifacts: '8', status: 'Running', statusClass: 'live' },
]

const artifacts = [
  { label: 'catalog:clean_dataset_v1', href: '#' },
  { label: 'report:quality_scorecard', href: '#' },
  { label: 'lineage:imputation_run_42', href: '#' },
  { label: 'benchmark:edge_suite_2026-05', href: '#' },
]

const benchmarks = [
  { label: 'Edge cases', value: '12' },
  { label: 'Success rate', value: '100%' },
  { label: 'Avg. pipeline', value: '1.8s' },
  { label: 'Peak memory', value: '242MB' },
]

const logs = [
  { stage: 'Intake', status: 'success', message: 'Object-store batch registered', timestamp: 'just now' },
  { stage: 'Publishing', status: 'success', message: 'Catalog artifacts updated', timestamp: '2m ago' },
  { stage: 'Benchmark', status: 'success', message: 'Edge-case suite completed', timestamp: '8m ago' },
]

function DashboardPage() {
  return (
    <div className="dashboard-page">
      <header className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Operations dashboard</h1>
          <p className="dashboard-subtitle">
            Monitor pipeline health, catalog publishing, and quality benchmarks. This environment writes to managed
            object storage and a metadata catalog, not local file system paths.
          </p>
          <div className="dashboard-tags">
            <span>Object storage</span>
            <span>Catalog-first</span>
            <span>Zero local files</span>
          </div>
        </div>
        <div className="nav-actions">
          <Link to="/upload" className="button button-primary">Open Upload</Link>
          <Link to="/benchmark" className="button button-secondary">Benchmark</Link>
          <Link to="/artifacts" className="button button-secondary button-secondary--ghost">Artifacts</Link>
          <Link to='/audio' className="button button-secondary button-secondary--ghost">Audio-Engine</Link>
        </div>
      </header>

      <main className="container dashboard-shell">
        <KPISection metrics={metrics} />

        <section className="dashboard-grid">
          <PipelineStatus stages={stages} />
          <ExecutionConsole logs={logs} />
        </section>

        <section className="dashboard-grid dashboard-grid--triple">
          {datasets.map((dataset) => (
            <DatasetCard key={dataset.id} dataset={dataset} />
          ))}
        </section>

        <section className="dashboard-grid">
          <ArtifactViewer artifacts={artifacts} />
          <BenchmarkCharts benchmarks={benchmarks} />
        </section>
      </main>
    </div>
  )
}

export default DashboardPage
