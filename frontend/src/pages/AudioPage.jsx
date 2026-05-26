import { useMemo, useState } from 'react'
import audioService from '../services/audioService'
import AudioVisualizer from '../components/AudioVisualizer/AudioVisualizer'

const phases = [
  'Upload',
  'Transcribe',
  'Extract Keywords',
  'Build Frequencies',
  'Cluster',
]

export default function AudioPage() {
  const [file, setFile] = useState(null)
  const [audioId, setAudioId] = useState(null)
  const [transcript, setTranscript] = useState('')
  const [keywords, setKeywords] = useState([])
  const [histogram, setHistogram] = useState({})
  const [clusters, setClusters] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [message, setMessage] = useState('Upload an audio file to generate transcript, keywords, and clusters automatically.')
  const [error, setError] = useState('')

  const handleFile = (e) => setFile(e.target.files?.[0] || null)

  const pipelineSteps = useMemo(() => {
    if (!audioId) return phases.map((phase) => ({ phase, status: 'idle' }))
    return phases.map((phase, idx) => ({
      phase,
      status: idx < 1 ? 'done' : 'ready',
    }))
  }, [audioId])

  const frequencyRows = useMemo(() => {
    return Object.entries(histogram || {})
      .map(([word, count]) => ({ word, count: Number(count) || 0 }))
      .sort((a, b) => b.count - a.count)
  }, [histogram])

  const runPipeline = async (uploadedAudioId) => {
    setIsRunning(true)
    setError('')
    try {
      setMessage('Transcribing audio automatically...')
      const transcriptRes = await audioService.postTranscription({ audio_id: uploadedAudioId })
      const transcriptText = transcriptRes?.transcript || transcriptRes?.text || ''
      setTranscript(transcriptText)

      setMessage('Extracting keywords and frequencies...')
      const extracted = await audioService.extractKeywords({ audio_id: uploadedAudioId, text: transcriptText })
      const freq = await audioService.computeFrequencies(uploadedAudioId, 50)
      setKeywords(extracted.keywords || [])
      setHistogram(freq.histogram || {})

      setMessage('Running clustering...')
      const clusterRes = await audioService.runClustering({ audio_id: uploadedAudioId, n_clusters: 3 })
      setClusters(clusterRes)

      setMessage('Audio pipeline complete. Transcript, keyword analytics, and clustering are ready.')
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'Pipeline failed')
      setMessage('Pipeline stopped. Check the error and retry.')
    } finally {
      setIsRunning(false)
    }
  }

  const upload = async () => {
    if (!file || isRunning) return
    setIsRunning(true)
    setError('')
    try {
      setMessage('Uploading audio...')
      const res = await audioService.uploadAudio(file)
      setAudioId(res.id)
      setMessage('Upload complete. Starting automatic transcription...')
      await runPipeline(res.id)
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'Upload failed')
      setMessage('Upload failed.')
    } finally {
      setIsRunning(false)
    }
  }

  const rerunPipeline = async () => {
    if (!audioId || isRunning) return
    await runPipeline(audioId)
  }

  const handleExport = async (datasetType, fmt) => {
    if (!audioId) return
    try {
      setMessage(`Preparing ${datasetType} export (${fmt})...`)
      const resp = await audioService.exportDataset(audioId, datasetType, fmt)
      const blob = new Blob([resp.data], { type: resp.headers['content-type'] || 'application/octet-stream' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      const disposition = resp.headers['content-disposition'] || ''
      let filename = ''
      const m = /filename\*=UTF-8''([^;]+)|filename="?([^;\"]+)"?/.exec(disposition)
      if (m) filename = decodeURIComponent(m[1] || m[2])
      if (!filename) filename = `${datasetType}_${audioId}.${fmt}`
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
      setMessage('Export ready. Check your downloads.')
    } catch (err) {
      setError(err?.response?.data?.error || err?.message || 'Export failed')
      setMessage('Export failed.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-slate-100 p-6 md:p-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-cyan-300/80">Database Accelerator</p>
              <h2 className="mt-2 text-3xl font-semibold md:text-5xl">Audio Dataset Engine</h2>
              <p className="mt-3 max-w-3xl text-slate-300">
                Upload audio once and let the backend handle transcription, keyword extraction, frequency analytics, and clustering.
                This is a feature inside the larger Database Accelerator workflow, not a separate transcription tool.
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100">
              <div className="font-medium">Status</div>
              <div className="mt-1 max-w-sm">{message}</div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white">Pipeline Control</h3>
            <p className="mt-2 text-sm text-slate-400">Choose an audio file. The app will trigger transcription automatically after upload.</p>

            <div className="mt-5 flex flex-col gap-4 rounded-2xl border border-dashed border-white/15 bg-white/5 p-5 md:flex-row md:items-center md:justify-between">
              <div>
                <label className="block text-sm font-medium text-slate-300">Audio file</label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFile}
                  className="mt-2 block w-full text-sm text-slate-200 file:mr-4 file:rounded-full file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-slate-950 hover:file:bg-cyan-300"
                />
              </div>
              <div className="flex gap-3">
                <button
                  className="rounded-full bg-cyan-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={upload}
                  disabled={!file || isRunning}
                >
                  {isRunning ? 'Processing...' : 'Upload & Run'}
                </button>
                <button
                  className="rounded-full border border-white/15 bg-white/5 px-5 py-3 font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={rerunPipeline}
                  disabled={!audioId || isRunning}
                >
                  Re-run Pipeline
                </button>
                {audioId && (
                  <div className="flex items-center gap-2">
                    <button
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:bg-white/10"
                      onClick={() => handleExport('keywords', 'csv')}
                    >
                      Export Keywords CSV
                    </button>
                    <button
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:bg-white/10"
                      onClick={() => handleExport('frequencies', 'csv')}
                    >
                      Export Frequencies CSV
                    </button>
                    <button
                      className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-white hover:bg-white/10"
                      onClick={() => handleExport('keywords', 'json')}
                    >
                      Export JSON
                    </button>
                  </div>
                )}
              </div>
            </div>

            {audioId && (
              <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-100">
                <span className="font-medium">Audio ID:</span> {audioId}
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">
                {error}
              </div>
            )}

            <div className="mt-6 grid gap-3 md:grid-cols-5">
              {pipelineSteps.map((step) => (
                <div key={step.phase} className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Step</div>
                  <div className="mt-1 text-sm font-semibold text-white">{step.phase}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white">Transcript</h3>
            <p className="mt-2 text-sm text-slate-400">Automatically generated by the backend transcription engine.</p>
            <div className="mt-4 min-h-48 rounded-2xl border border-white/10 bg-slate-900/80 p-4 text-sm leading-6 text-slate-200">
              {transcript || 'Transcript will appear here after processing.'}
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Keyword Frequencies</h3>
                <p className="mt-1 text-sm text-slate-400">Top keyword histogram from the extracted transcript.</p>
              </div>
            </div>
            <div className="mt-4 h-[340px]">
              <AudioVisualizer type="bar" data={histogram} />
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white">Top Keywords</h3>
            <div className="mt-4 space-y-3">
              {keywords.length > 0 ? keywords.map((k) => (
                <div key={k.keyword} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <span className="font-medium text-white">{k.keyword}</span>
                  <span className="rounded-full bg-cyan-400/15 px-3 py-1 text-sm font-semibold text-cyan-200">{k.frequency}</span>
                </div>
              )) : (
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                  No keywords yet. Upload and process an audio file first.
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
          <h3 className="text-lg font-semibold text-white">Word Frequency Table</h3>
          <p className="mt-1 text-sm text-slate-400">Sorted frequency counts generated from the backend analytics response.</p>
          <div className="mt-4 overflow-auto rounded-2xl border border-white/10 bg-slate-900/80">
            <table className="min-w-full text-left text-sm text-slate-200">
              <thead className="bg-white/5 text-xs uppercase tracking-[0.15em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Word</th>
                  <th className="px-4 py-3">Frequency</th>
                </tr>
              </thead>
              <tbody>
                {frequencyRows.length > 0 ? (
                  frequencyRows.map((row) => (
                    <tr key={row.word} className="border-t border-white/10">
                      <td className="px-4 py-3 font-medium text-white">{row.word}</td>
                      <td className="px-4 py-3">{row.count}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-4 py-4 text-slate-400" colSpan={2}>
                      No frequency data yet. Upload and process audio to populate this table.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 shadow-xl">
          <h3 className="text-lg font-semibold text-white">Cluster Output</h3>
          <p className="mt-1 text-sm text-slate-400">The backend groups keywords into semantic clusters after extraction.</p>
          <div className="mt-4 overflow-auto rounded-2xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-200">
            <pre className="whitespace-pre-wrap">{clusters ? JSON.stringify(clusters, null, 2) : 'Cluster results will appear here after the pipeline completes.'}</pre>
          </div>
        </section>
      </div>
    </div>
  )
}
