import api from './index'

export interface PlatformStat {
  name: string
  slug: string
  count: number
}

export interface Stats {
  total_roms: number
  total_platforms: number
  total_size_bytes: number
  roms_with_igdb: number
  roms_with_screenscraper: number
  scrape_coverage: number
  top_platforms: PlatformStat[]
  last_scan: string | null
}

export const getStats = async (): Promise<Stats> => {
  const response = await api.get<Stats>('/roms/stats')
  return response.data
}
