import axios from 'axios'

export const API_BASE_URL = 'http://localhost:8000/api'

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
