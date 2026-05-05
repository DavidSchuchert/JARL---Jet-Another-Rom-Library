import api from './index'

export interface Rom {
  id: number
  filename: string
  title: string
  platform_slug: string
  region: string | null
  year: number | null
  genre: string | null
  players: string | null
  developer: string | null
  description: string | null
  publisher: string | null
  cover_url: string | null
  size: number
  path: string
  hash_sha1: string | null
  scrape_status: string
  created_at: string
  updated_at: string
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
}

export const getRoms = async (params: GetRomsParams = {}): Promise<RomsResponse> => {
  const response = await api.get<RomsResponse>('/roms', { params })
  return response.data
}

export const getRom = async (id: number): Promise<Rom> => {
  const response = await api.get<Rom>(`/roms/${id}`)
  return response.data
}

export const deleteRom = async (id: number): Promise<void> => {
  await api.delete(`/roms/${id}`)
}
