import api from './index'

export interface Rom {
  id: number
  filename: string
  title: string
  platform_slug: string
  region: string | null
  year: number | null
  release_date: string | null
  genre: string | null
  players: string | null
  developer: string | null
  description: string | null
  publisher: string | null
  cover_url: string | null
  screenshots: string | null    // JSON string: list of local paths
  rating: number | null         // 0-100
  languages: string | null      // JSON string: list of language names
  version: string | null
  size: number
  path: string
  hash_sha1: string | null
  scrape_status: string
  is_multi_disc: boolean
  disc_count: number | null
  created_at: string
  updated_at: string
}

export interface RomUpdatePayload {
  title?: string
  description?: string
  year?: number | null
  release_date?: string | null
  developer?: string | null
  publisher?: string | null
  genre?: string | null
  players?: string | null
  region?: string | null
  cover_url?: string | null
  rating?: number | null
}

export interface RomsResponse {
  items: Rom[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface GetRomsParams {
  page?: number
  page_size?: number
  search?: string
  platform?: string
  region?: string
  year?: number
  genre?: string
  sort_by?: 'title' | 'year' | 'rating' | 'size' | 'scrape_status'
  sort_dir?: 'asc' | 'desc'
}

export const getRoms = async (params: GetRomsParams = {}): Promise<RomsResponse> => {
  const response = await api.get<RomsResponse>('/roms', { params })
  return response.data
}

export const getRom = async (id: number): Promise<Rom> => {
  const response = await api.get<Rom>(`/roms/${id}`)
  return response.data
}

export const updateRom = async (id: number, payload: RomUpdatePayload): Promise<Rom> => {
  const response = await api.patch<Rom>(`/roms/${id}`, payload)
  return response.data
}

export const deleteRom = async (id: number): Promise<void> => {
  await api.delete(`/roms/${id}`)
}
