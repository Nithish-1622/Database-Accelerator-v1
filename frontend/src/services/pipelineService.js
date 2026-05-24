import uploadService from './uploadService'

export const pipelineService = {
  runAcceleratorPipeline: uploadService.runAcceleratorPipeline,
  getCombinedReport: uploadService.getCombinedReport,
}

export default pipelineService
