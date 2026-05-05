import api from './index'

export interface ScrapeStatus {
  status: 'idle' | 'running' | 'completed' | 'failed'
  total: number
  done: number
  success: number
  failed: number
  skipped: number
  current_file: string | null
  percent: number
  errors: string[]
}

export const startScrape = async (platform?: string, onlyMissing: boolean = true) => {
  const response = await api.post('/scrape/start', null, {
    params: {
      platform,
      only_missing: onlyMissing
    }
  })
  return response.data
}

export const rescrapeRom = async (romId: number) => {
  const response = await api.post(`/scrape/rom/${romId}`)
  return response.data
}

export const getScrapeStatus = async (): Promise<ScrapeStatus> => {
  const response = await api.get('/scrape/status')
  return response.data
}

export const stopScrape = async () => {
  const response = await api.post('/scrape/stop')
  return response.data
}
