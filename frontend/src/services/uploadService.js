import axios from 'axios'

const resolveApiBaseUrl = () => {
  const configured = import.meta.env.VITE_API_BASE_URL
  if (configured) return configured

  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000/api'
    }
  }

  return '/_/backend/api'
}

export const API_BASE_URL = resolveApiBaseUrl()

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadDataset = async (file) => {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await client.post('/upload/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getDatasetMetadata = async (datasetId) => {
  try {
    const response = await client.get(`/upload/${datasetId}/metadata/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const listDatasets = async () => {
  try {
    const response = await client.get('/upload/list_datasets/')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const analyzeDataset = async (datasetId) => {
  try {
    const response = await client.post(`/analyze/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getAnalysisReport = async (datasetId) => {
  try {
    const response = await client.get(`/analyze/${datasetId}/report/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const preprocessDataset = async (datasetId) => {
  try {
    const response = await client.post(`/preprocess/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getPreprocessingReport = async (datasetId) => {
  try {
    const response = await client.get(`/preprocess/${datasetId}/report/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const exportDataset = async (datasetId) => {
  try {
    const response = await client.post(`/export/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getExportReport = async (datasetId) => {
  try {
    const response = await client.get(`/export/${datasetId}/report/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getCombinedReport = async (datasetId) => {
  try {
    const response = await client.get(`/reports/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const generateIntelligenceReport = async (datasetId) => {
  try {
    const response = await client.post(`/intelligence/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getIntelligenceReport = async (datasetId) => {
  try {
    const response = await client.get(`/intelligence/${datasetId}/report/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const listReports = async () => {
  try {
    const response = await client.get('/reports/list/')
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const runAcceleratorPipeline = async (datasetId) => {
  try {
    const response = await client.post(`/accelerator/run/${datasetId}/`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

export const getAcceleratorArtifactUrl = (datasetId, artifactName) => {
  const safeArtifactName = encodeURIComponent(artifactName)
  return `${API_BASE_URL}/accelerator/artifact/${datasetId}/${safeArtifactName}/`
}

export const uploadService = {
  uploadDataset,
  getDatasetMetadata,
  listDatasets,
  analyzeDataset,
  getAnalysisReport,
  preprocessDataset,
  getPreprocessingReport,
  exportDataset,
  getExportReport,
  getCombinedReport,
  generateIntelligenceReport,
  getIntelligenceReport,
  listReports,
  runAcceleratorPipeline,
  getAcceleratorArtifactUrl,
}

export default uploadService
