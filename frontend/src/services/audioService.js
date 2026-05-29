import axios from 'axios'
import { API_BASE_URL } from './api'

const client = axios.create({ baseURL: API_BASE_URL })

export const uploadAudio = async (file) => {
  const form = new FormData()
  form.append('audio_file', file)
  const resp = await client.post('/audio/upload/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
  return resp.data
}

export const getAudioStatus = async (audioId) => {
  const resp = await client.get(`/audio/status/${audioId}/`)
  return resp.data
}

export const postTranscription = async ({ audio_id, transcript_override, model_name }) => {
  const resp = await client.post('/audio/transcript/', { audio_id, transcript_override, model_name })
  return resp.data
}

export const extractKeywords = async ({ audio_id, text }) => {
  const resp = await client.post('/audio/keywords/', { audio_id, text })
  return resp.data
}

export const listKeywords = async (audio_id) => {
  const resp = await client.get(`/audio/keywords/list/?audio_id=${audio_id}`)
  return resp.data
}

export const listFrequencies = async (audio_id) => {
  const resp = await client.get(`/audio/frequencies/?audio_id=${audio_id}`)
  return resp.data
}

export const computeFrequencies = async (audio_id, top_k = 50) => {
  const resp = await client.get(`/audio/frequencies/compute/?audio_id=${audio_id}&top_k=${top_k}`)
  return resp.data
}

export const runClustering = async ({
  audio_id,
  n_clusters = 3,
  algorithm = 'kmeans',
  eps = 0.5,
  min_samples = 2,
}) => {
  const resp = await client.post('/audio/clusters/', { audio_id, n_clusters, algorithm, eps, min_samples })
  return resp.data
}

export const exportDataset = async (audio_id, datasetType = 'keywords', format = 'csv') => {
  const resp = await client.get(`/audio/export/${audio_id}/${datasetType}/${format}/`, { responseType: 'blob' })
  return resp
}

const audioService = {
  uploadAudio,
  getAudioStatus,
  postTranscription,
  extractKeywords,
  listKeywords,
  listFrequencies,
  computeFrequencies,
  runClustering,
  exportDataset,
}

export default audioService
