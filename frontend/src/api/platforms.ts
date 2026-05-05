import api from './index'

export interface Platform {
  id: number
  name: string
  slug: string
  icon: string | null
  rom_count: number
  family: string | null
}

export const getPlatforms = async (): Promise<Platform[]> => {
  const response = await api.get<Platform[]>('/platforms')
  return response.data
}

export const getPlatform = async (slug: string): Promise<Platform> => {
  const response = await api.get<Platform>(`/platforms/${slug}`)
  return response.data
}
