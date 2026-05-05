import api from './index'

export interface ScanProgress {
  status: 'idle' | 'running' | 'completed' | 'failed'
  total_files: number
  scanned_files: number
  current_file: string | null
  errors: number
  started_at: string | null
  completed_at: string | null
}

export interface ScanJob {
  id: number
  status: ScanProgress['status']
  progress: ScanProgress
}

export interface ScanEvent {
  sequence: number
  type: 'info' | 'file' | 'success' | 'error'
  message: string
  current_file: string | null
  scanned_files: number | null
  created_at: string
}

interface ScanStartResponse {
  job_id: number
  status: 'started'
  message: string
}

interface ScanJobResponse {
  id: number
  status: ScanProgress['status']
  total_files: number
  scanned_files: number
  current_file: string | null
  errors: number
  started_at: string
  completed_at: string | null
  progress_percentage: number
}

const toScanJob = (job: ScanJobResponse): ScanJob => ({
  id: job.id,
  status: job.status,
  progress: {
    status: job.status,
    total_files: job.total_files,
    scanned_files: job.scanned_files,
    current_file: job.current_file,
    errors: job.errors,
    started_at: job.started_at,
    completed_at: job.completed_at
  }
})

export const startScan = async (fullScan: boolean = false): Promise<ScanJob> => {
  const response = await api.post<ScanStartResponse>('/scan/start', null, {
    params: { full_scan: fullScan }
  })
  return {
    id: response.data.job_id,
    status: 'running',
    progress: {
      status: 'running',
      total_files: 0,
      scanned_files: 0,
      current_file: null,
      errors: 0,
      started_at: null,
      completed_at: null
    }
  }
}

export const getScanStatus = async (jobId: number): Promise<ScanJob> => {
  const response = await api.get<ScanJobResponse>(`/scan/status/${jobId}`)
  return toScanJob(response.data)
}

export const getScanEvents = async (jobId: number, after: number = 0): Promise<ScanEvent[]> => {
  const response = await api.get<ScanEvent[]>(`/scan/events/${jobId}`, {
    params: { after }
  })
  return response.data
}

export const getCurrentScanJob = async (): Promise<ScanJob | null> => {
  const response = await api.get<{ current_job: ScanJobResponse | null }>('/scan/progress')
  if (!response.data.current_job) return null
  return toScanJob(response.data.current_job)
}

export const getScanProgress = async (): Promise<ScanProgress> => {
  const response = await api.get<{ current_job: ScanJobResponse | null }>('/scan/progress')
  if (!response.data.current_job) {
    return {
      status: 'idle',
      total_files: 0,
      scanned_files: 0,
      current_file: null,
      errors: 0,
      started_at: null,
      completed_at: null
    }
  }
  return toScanJob(response.data.current_job).progress
}
