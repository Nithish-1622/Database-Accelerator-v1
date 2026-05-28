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

export const api = {
  get: (url) => client.get(url),
  post: (url, data) => client.post(url, data),
  put: (url, data) => client.put(url, data),
  delete: (url) => client.delete(url),
  runAccelerator: (datasetId) => client.post(`/accelerator/run/${datasetId}/`),
  acceleratorArtifactUrl: (datasetId, artifactName) => (
    `${API_BASE_URL}/accelerator/artifact/${datasetId}/${encodeURIComponent(artifactName)}/`
  ),
}

export const uploadDataset = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await axios.post(
      `${API_BASE_URL}/upload/upload/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message)
  }
}

export default client
