import uploadService from './uploadService'

export const datasetService = {
  listDatasets: uploadService.listDatasets,
  getDatasetMetadata: uploadService.getDatasetMetadata,
  analyzeDataset: uploadService.analyzeDataset,
  preprocessDataset: uploadService.preprocessDataset,
}

export default datasetService
