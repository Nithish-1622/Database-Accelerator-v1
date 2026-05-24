import { useState } from 'react'
import {
  uploadDataset,
  analyzeDataset,
  getAnalysisReport,
  preprocessDataset,
  getPreprocessingReport,
  exportDataset,
  getExportReport,
  getCombinedReport,
  generateIntelligenceReport,
  getIntelligenceReport,
  runAcceleratorPipeline,
  getAcceleratorArtifactUrl,
} from '../services/uploadService'
import './UploadPage.css'

function UploadPage() {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const [error, setError] = useState('')
  const [datasets, setDatasets] = useState([])
  const [analysisReports, setAnalysisReports] = useState({})
  const [preprocessingReports, setPreprocessingReports] = useState({})
  const [exportReports, setExportReports] = useState({})
  const [combinedReports, setCombinedReports] = useState({})
  const [intelligenceReports, setIntelligenceReports] = useState({})
  const [acceleratorRuns, setAcceleratorRuns] = useState({})
  const [datasetLogs, setDatasetLogs] = useState({})
  const [analyzingId, setAnalyzingId] = useState('')
  const [preprocessingId, setPreprocessingId] = useState('')
  const [exportingId, setExportingId] = useState('')
  const [intelligenceId, setIntelligenceId] = useState('')
  const [acceleratorId, setAcceleratorId] = useState('')

  const totalLogs = Object.values(datasetLogs).reduce((count, logs) => count + logs.length, 0)
  const acceleratorRunCount = Object.keys(acceleratorRuns).length
  const datasetCount = datasets.length

  const getErrorMessage = (err, fallback) => {
    if (!err) return fallback
    if (typeof err === 'string') return err
    if (err.error) return err.error
    if (err.message) return err.message
    return fallback
  }

  const addDatasetLog = (datasetId, stage, level, message, details = null) => {
    const timestamp = new Date().toLocaleTimeString()
    const logEntry = { timestamp, stage, level, message, details }

    setDatasetLogs((currentLogs) => {
      const logsForDataset = currentLogs[datasetId] || []
      const nextLogs = [logEntry, ...logsForDataset].slice(0, 24)
      return {
        ...currentLogs,
        [datasetId]: nextLogs,
      }
    })
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      setFile(droppedFile)
      setError('')
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload')
      return
    }

    setUploading(true)
    setUploadStatus('Uploading file...')
    setError('')

    try {
      const result = await uploadDataset(file)
      
      if (result.id) {
        setUploadStatus('File uploaded successfully!')
        const nextDatasets = [result, ...datasets]
        setDatasets(nextDatasets)
        addDatasetLog(result.id, 'Upload', 'info', 'Dataset uploaded to filesystem', {
          filename: result.filename,
          rows: result.rows,
          columns: result.columns,
          fileType: result.file_type,
        })
        setFile(null)

        try {
          setAnalyzingId(result.id)
          setUploadStatus('File uploaded. Running analysis...')
          const analysis = await analyzeDataset(result.id)
          setAnalysisReports((currentReports) => ({
            ...currentReports,
            [result.id]: analysis,
          }))
          addDatasetLog(result.id, 'Analyze', 'info', 'Analysis completed', {
            completeness: analysis.completeness_score,
            missingCells: analysis.missing_cells,
            duplicateRows: analysis.duplicate_rows,
          })

          const report = await getAnalysisReport(result.id)
          setAnalysisReports((currentReports) => ({
            ...currentReports,
            [result.id]: report,
          }))
          updateDataset(result.id, { status: 'analyzed' })
          setUploadStatus('File uploaded and analyzed successfully!')
        } finally {
          setAnalyzingId('')
        }
        
        // Clear the upload status after 3 seconds
        setTimeout(() => {
          setUploadStatus('')
        }, 3000)
      } else {
        setError('Upload failed. Please try again.')
      }
    } catch (err) {
      setError(getErrorMessage(err, 'An error occurred during upload'))
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes, k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const updateDataset = (datasetId, updates) => {
    setDatasets((currentDatasets) =>
      currentDatasets.map((dataset) =>
        dataset.id === datasetId ? { ...dataset, ...updates } : dataset
      )
    )
  }

  const mergeCombinedReport = (datasetId, reportKey, reportValue) => {
    setCombinedReports((currentReports) => {
      const currentEntry = currentReports[datasetId]
      return {
        ...currentReports,
        [datasetId]: currentEntry
          ? { ...currentEntry, [reportKey]: reportValue }
          : { [reportKey]: reportValue },
      }
    })
  }

  const runAnalysis = async (datasetId) => {
    try {
      setAnalyzingId(datasetId)
      addDatasetLog(datasetId, 'Analyze', 'info', 'Analysis started')
      const analysis = await analyzeDataset(datasetId)
      setAnalysisReports((currentReports) => ({ ...currentReports, [datasetId]: analysis }))
      const report = await getAnalysisReport(datasetId)
      setAnalysisReports((currentReports) => ({ ...currentReports, [datasetId]: report }))
      mergeCombinedReport(datasetId, 'analysis_report', report)
      updateDataset(datasetId, { status: 'analyzed' })
      addDatasetLog(datasetId, 'Analyze', 'success', 'Analysis report available', {
        completeness: report.completeness_score,
        missingCells: report.missing_cells,
        duplicateRows: report.duplicate_rows,
      })
    } catch (analysisError) {
      const message = getErrorMessage(analysisError, 'Analysis failed')
      setError(message)
      addDatasetLog(datasetId, 'Analyze', 'error', message)
    } finally {
      setAnalyzingId('')
    }
  }

  const runPreprocessing = async (datasetId) => {
    try {
      setPreprocessingId(datasetId)
      addDatasetLog(datasetId, 'Clean', 'info', 'Preprocessing started')
      const preprocessing = await preprocessDataset(datasetId)
      setPreprocessingReports((currentReports) => ({ ...currentReports, [datasetId]: preprocessing }))
      const report = await getPreprocessingReport(datasetId)
      setPreprocessingReports((currentReports) => ({ ...currentReports, [datasetId]: report }))
      mergeCombinedReport(datasetId, 'cleaning_report', report)
      updateDataset(datasetId, { status: 'processed' })
      addDatasetLog(datasetId, 'Clean', 'success', 'Preprocessing report available', {
        originalRows: report.original_rows,
        cleanedRows: report.cleaned_rows,
        duplicatesRemoved: report.duplicates_removed,
      })
    } catch (preprocessingError) {
      const message = getErrorMessage(preprocessingError, 'Preprocessing failed')
      setError(message)
      addDatasetLog(datasetId, 'Clean', 'error', message)
    } finally {
      setPreprocessingId('')
    }
  }

  const runIntelligence = async (datasetId) => {
    try {
      setIntelligenceId(datasetId)
      addDatasetLog(datasetId, 'Intelligence', 'info', 'Pattern discovery started')
      const intelligence = await generateIntelligenceReport(datasetId)
      setIntelligenceReports((currentReports) => ({ ...currentReports, [datasetId]: intelligence }))
      const report = await getIntelligenceReport(datasetId)
      setIntelligenceReports((currentReports) => ({ ...currentReports, [datasetId]: report }))
      mergeCombinedReport(datasetId, 'intelligence_report', report)
      addDatasetLog(datasetId, 'Intelligence', 'success', 'Intelligence report available', {
        numericColumns: report.numeric_columns?.length || 0,
        categoricalColumns: report.categorical_columns?.length || 0,
        strongCorrelations: report.strong_correlations?.length || 0,
      })
    } catch (intelligenceError) {
      const message = getErrorMessage(intelligenceError, 'Intelligence failed')
      setError(message)
      addDatasetLog(datasetId, 'Intelligence', 'error', message)
    } finally {
      setIntelligenceId('')
    }
  }

  const runExport = async (datasetId) => {
    try {
      setExportingId(datasetId)
      addDatasetLog(datasetId, 'Export', 'info', 'Export started')
      const exportResult = await exportDataset(datasetId)
      setExportReports((currentReports) => ({ ...currentReports, [datasetId]: exportResult }))
      const report = await getExportReport(datasetId)
      setExportReports((currentReports) => ({ ...currentReports, [datasetId]: report }))
      mergeCombinedReport(datasetId, 'export_report', report)
      updateDataset(datasetId, { status: 'exported' })
      addDatasetLog(datasetId, 'Export', 'success', 'Export report available', {
        exportFilename: report.export_filename,
        exportedAt: report.exported_at,
      })
    } catch (exportError) {
      const message = getErrorMessage(exportError, 'Export failed')
      setError(message)
      addDatasetLog(datasetId, 'Export', 'error', message)
    } finally {
      setExportingId('')
    }
  }

  const runAccelerator = async (datasetId) => {
    try {
      setAcceleratorId(datasetId)
      addDatasetLog(datasetId, 'Accelerator', 'info', 'Full pipeline run started')
      const result = await runAcceleratorPipeline(datasetId)
      setAcceleratorRuns((currentRuns) => ({ ...currentRuns, [datasetId]: result }))
      updateDataset(datasetId, { status: 'optimized' })
      addDatasetLog(datasetId, 'Accelerator', 'success', 'Pipeline completed and artifacts generated', {
        qualityBefore: result.quality_before?.health_score,
        qualityAfter: result.quality_after?.health_score,
        removedColumns: result.removed_columns_count,
      })
    } catch (acceleratorError) {
      const message = getErrorMessage(acceleratorError, 'Accelerator pipeline failed')
      setError(message)
      addDatasetLog(datasetId, 'Accelerator', 'error', message)
    } finally {
      setAcceleratorId('')
    }
  }

  const loadCombinedReport = async (datasetId) => {
    try {
      const report = await getCombinedReport(datasetId)
      setCombinedReports((currentReports) => ({ ...currentReports, [datasetId]: report }))
      addDatasetLog(datasetId, 'Reports', 'success', 'Combined report synchronized')
    } catch (reportError) {
      const message = getErrorMessage(reportError, 'Failed to load combined report')
      setError(message)
      addDatasetLog(datasetId, 'Reports', 'error', message)
    }
  }

  return (
    <div className="upload-page">
      <nav className="navbar navbar--workspace">
        <div>
          <p className="eyebrow">Dataset workspace</p>
          <h1>Upload and prepare data</h1>
        </div>
        <div className="workspace-status">
          <span className="status-pill status-pill--live">Filesystem storage</span>
          <span className="status-pill">No database dependency</span>
        </div>
      </nav>

      <main className="container upload-layout upload-layout--dashboard">
        <section className="dashboard-summary card">
          <div className="dashboard-summary__copy">
            <p className="eyebrow">Operations dashboard</p>
            <h2>Production-grade dataset accelerator</h2>
            <p>
              Upload once, then track analysis, cleaning, intelligence, exports, logs, and the full accelerator pipeline from a single workspace.
            </p>
          </div>

          <div className="dashboard-summary__metrics">
            <article>
              <span>Datasets</span>
              <strong>{datasetCount}</strong>
            </article>
            <article>
              <span>Accelerator runs</span>
              <strong>{acceleratorRunCount}</strong>
            </article>
            <article>
              <span>Log entries</span>
              <strong>{totalLogs}</strong>
            </article>
            <article>
              <span>Mode</span>
              <strong>Filesystem</strong>
            </article>
          </div>
        </section>

        <section className="upload-panel card upload-panel--hero">
          <div className="section-heading section-heading--compact">
            <p className="eyebrow">Ingestion</p>
            <h2>Upload a dataset</h2>
            <p>Drag and drop a file or browse from your machine. Uploaded files stay on disk and feed every downstream stage.</p>
          </div>

          <label
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            htmlFor="dataset-file-input"
            aria-label="Dataset file upload area"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="drop-zone-content">
              <div className="drop-icon-wrap">
                <p className="icon">⬆</p>
              </div>
              <p className="text">Drop files here</p>
              <p className="subtext">or use the file picker below</p>
              <input
                id="dataset-file-input"
                type="file"
                onChange={handleFileChange}
                accept=".csv,.xlsx,.xls,.json"
                disabled={uploading}
                style={{ display: 'none' }}
              />
              <span className="file-input-label">Choose a file</span>
              <p className="formats">CSV, XLSX, XLS, JSON supported</p>
            </div>
          </label>

          {file && (
            <div className="file-info file-info--selected">
              <div className="file-info__header">
                <div>
                  <p className="eyebrow">Selected file</p>
                  <h3>{file.name}</h3>
                </div>
                <span className="status-pill status-pill--live">Ready to upload</span>
              </div>
              <div className="file-details file-details--grid">
                <div>
                  <span>Size</span>
                  <strong>{formatFileSize(file.size)}</strong>
                </div>
                <div>
                  <span>Type</span>
                  <strong>{file.type || 'Unknown'}</strong>
                </div>
              </div>
              <button
                className="button button-primary button-primary--full"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? 'Uploading…' : 'Upload and analyze'}
              </button>
            </div>
          )}

          {uploadStatus && (
            <div className="success-message">
              {uploadStatus}
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </section>

        {/* Sidebar removed for product-style dashboard; focus on operator KPIs */}

        <section className="datasets-section card datasets-panel">
          <div className="section-heading section-heading--compact">
            <p className="eyebrow">Workspace</p>
            <h2>Recent datasets</h2>
            <p>Every upload becomes a managed dataset with analysis, preprocessing, intelligence, and export controls. Use the action buttons to run stages and access artifacts.</p>
          </div>

          {datasets.length > 0 ? (
            <div className="datasets-grid">
              {datasets.map((dataset) => (
                <article key={dataset.id} className="dataset-card dataset-card--modern">
                  <div className="dataset-card__header">
                    <div>
                      <p className="eyebrow">{dataset.file_type.toUpperCase()}</p>
                      <h4>{dataset.filename}</h4>
                    </div>
                    <span className={`status-pill status-pill--${dataset.status}`}>{dataset.status}</span>
                  </div>

                  <div className="dataset-info dataset-info--grid">
                    <div><span>Rows</span><strong>{dataset.rows}</strong></div>
                    <div><span>Columns</span><strong>{dataset.columns}</strong></div>
                    <div><span>Size</span><strong>{dataset.file_size_mb} MB</strong></div>
                    <div><span>Updated</span><strong>{dataset.updated_at?.slice(0, 19)?.replace('T', ' ')}</strong></div>
                  </div>

                  <div className="action-grid">
                    <button className="button button-secondary" disabled={analyzingId === dataset.id} onClick={() => runAnalysis(dataset.id)}>
                      {analyzingId === dataset.id ? 'Analyzing…' : 'Analyze'}
                    </button>

                    <button className="button button-secondary" disabled={preprocessingId === dataset.id} onClick={() => runPreprocessing(dataset.id)}>
                      {preprocessingId === dataset.id ? 'Cleaning…' : 'Clean'}
                    </button>

                    <button className="button button-secondary" disabled={intelligenceId === dataset.id} onClick={() => runIntelligence(dataset.id)}>
                      {intelligenceId === dataset.id ? 'Discovering…' : 'Intelligence'}
                    </button>

                    <button className="button button-secondary" disabled={exportingId === dataset.id} onClick={() => runExport(dataset.id)}>
                      {exportingId === dataset.id ? 'Exporting…' : 'Export'}
                    </button>

                    <button className="button button-secondary" onClick={() => loadCombinedReport(dataset.id)}>
                      Reports
                    </button>

                    <button className="button button-primary" disabled={acceleratorId === dataset.id} onClick={() => runAccelerator(dataset.id)}>
                      {acceleratorId === dataset.id ? 'Running Pipeline…' : 'Run Accelerator'}
                    </button>
                  </div>

                  <div className="report-stack">
                    {analysisReports[dataset.id] && (
                      <div className="analysis-summary">
                        <p><strong>Analysis</strong></p>
                        <p>Completeness {analysisReports[dataset.id].completeness_score}% · Missing {analysisReports[dataset.id].missing_cells} · Duplicates {analysisReports[dataset.id].duplicate_rows}</p>
                      </div>
                    )}

                    {preprocessingReports[dataset.id] && (
                      <div className="analysis-summary">
                        <p><strong>Cleaning</strong></p>
                        <p>{preprocessingReports[dataset.id].original_rows} rows → {preprocessingReports[dataset.id].cleaned_rows} rows · {preprocessingReports[dataset.id].duplicates_removed} removed</p>
                      </div>
                    )}

                    {intelligenceReports[dataset.id] && (
                      <div className="analysis-summary">
                        <p><strong>Intelligence</strong></p>
                        <p>{intelligenceReports[dataset.id].numeric_columns?.length || 0} numeric · {intelligenceReports[dataset.id].categorical_columns?.length || 0} categorical · {intelligenceReports[dataset.id].strong_correlations?.length || 0} strong correlations</p>
                      </div>
                    )}

                    {exportReports[dataset.id] && (
                      <div className="analysis-summary">
                        <p><strong>Export</strong></p>
                        <p>{exportReports[dataset.id].export_filename} · {exportReports[dataset.id].exported_at}</p>
                      </div>
                    )}

                    {combinedReports[dataset.id] && (
                      <div className="analysis-summary">
                        <p><strong>Combined report available</strong></p>
                      </div>
                    )}

                    {acceleratorRuns[dataset.id] && (
                      <section className="accelerator-summary">
                        <header className="accelerator-summary__header">
                          <p className="eyebrow">Accelerator Run</p>
                          <h5>Pipeline Intelligence</h5>
                        </header>
                        <div className="kpi-grid">
                          <div>
                            <span>Schema</span>
                            <strong>{acceleratorRuns[dataset.id].schema_detection?.rows || 0} rows / {acceleratorRuns[dataset.id].schema_detection?.columns || 0} cols</strong>
                          </div>
                          <div>
                            <span>Health Score</span>
                            <strong>{acceleratorRuns[dataset.id].quality_before?.health_score}% → {acceleratorRuns[dataset.id].quality_after?.health_score}%</strong>
                          </div>
                          <div>
                            <span>Correlations</span>
                            <strong>{acceleratorRuns[dataset.id].pattern_discovery?.pearson?.length || 0} Pearson pairs</strong>
                          </div>
                          <div>
                            <span>Removed Columns</span>
                            <strong>{acceleratorRuns[dataset.id].removed_columns_count}</strong>
                          </div>
                        </div>

                        <div className="artifact-grid">
                          {Object.keys(acceleratorRuns[dataset.id].artifacts || {}).map((artifactName) => (
                            <a
                              key={artifactName}
                              className="artifact-link"
                              href={getAcceleratorArtifactUrl(dataset.id, artifactName)}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {artifactName}
                            </a>
                          ))}
                        </div>
                      </section>
                    )}

                    <section className="execution-console">
                      <header className="execution-console__header">
                        <p className="eyebrow">Execution Console</p>
                        <span>{(datasetLogs[dataset.id] || []).length} logs</span>
                      </header>
                      <div className="execution-log-list">
                        {(datasetLogs[dataset.id] || []).length > 0 ? (
                          datasetLogs[dataset.id].map((entry, index) => (
                            <div key={`${dataset.id}-log-${index}`} className={`execution-log execution-log--${entry.level}`}>
                              <div className="execution-log__meta">
                                <strong>{entry.stage}</strong>
                                <span>{entry.timestamp}</span>
                              </div>
                              <p>{entry.message}</p>
                              {entry.details && (
                                <pre>{JSON.stringify(entry.details, null, 2)}</pre>
                              )}
                            </div>
                          ))
                        ) : (
                          <p className="execution-empty">Run a stage to view backend execution telemetry.</p>
                        )}
                      </div>
                    </section>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <h3>No datasets yet</h3>
              <p>Upload a file to see a structured workspace with analysis, cleaning, intelligence, and export actions.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default UploadPage
