import { Link } from 'react-router-dom'
import KPISection from '../components/KPISection/KPISection'
import ExecutionConsole from '../components/ExecutionConsole/ExecutionConsole'
import DatasetCard from '../components/DatasetCard/DatasetCard'
import ArtifactViewer from '../components/ArtifactViewer/ArtifactViewer'
import PipelineStatus from '../components/PipelineStatus/PipelineStatus'
import BenchmarkCharts from '../components/BenchmarkCharts/BenchmarkCharts'
import './DashboardPage.css'

const metrics = [
  { label: 'Datasets', value: '128' },
  { label: 'Running', value: '07' },
  { label: 'Artifacts', value: '564' },
  { label: 'Benchmark score', value: '98.4%' },
]

const stages = [
  { label: 'Registration' },
  { label: 'Ingestion' },
  { label: 'Quality profiling' },
  { label: 'Imputation' },
  { label: 'Export' },
]

const datasets = [
  { id: 'ds-01', name: 'Customer churn refresh', description: 'High-volume nightly batch', rows: '120K', artifacts: '6', status: 'Ready', statusClass: 'ready' },
  { id: 'ds-02', name: 'Product telemetry', description: 'Streaming export snapshot', rows: '45K', artifacts: '8', status: 'Running', statusClass: 'live' },
]

const artifacts = [
  { label: 'clean_dataset.csv', href: '#' },
  { label: 'quality_report.pdf', href: '#' },
  { label: 'imputation_log.json', href: '#' },
  { label: 'benchmark_report.json', href: '#' },
]

const benchmarks = [
  { label: 'Edge cases', value: '12' },
  { label: 'Success rate', value: '100%' },
  { label: 'Avg. pipeline', value: '1.8s' },
  { label: 'Peak memory', value: '242MB' },
]

const logs = [
  { stage: 'Ingestion', status: 'success', message: 'Latest upload registered successfully', timestamp: 'just now' },
  { stage: 'Export', status: 'success', message: 'Artifact bundle published', timestamp: '2m ago' },
  { stage: 'Benchmark', status: 'success', message: 'Edge-case suite completed', timestamp: '8m ago' },
]

function DashboardPage() {
  return (
    <div className="dashboard-page">
      <header className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Database Accelerator</p>
          <h1>Operations dashboard</h1>
        </div>
        <div className="nav-actions">
          <Link to="/upload" className="button button-primary">Open Upload</Link>
          <Link to="/benchmark" className="button button-secondary">Benchmark</Link>
          <Link to="/artifacts" className="button button-secondary button-secondary--ghost">Artifacts</Link>
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
