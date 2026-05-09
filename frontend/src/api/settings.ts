import api from './index'

export interface ScraperAuthResult {
  status: 'success' | 'failed' | 'error'
  message: string
  http_code?: number
  user?: string
  client_id?: string
}

export interface ScraperAuthStatus {
  screenscraper?: ScraperAuthResult
  igdb?: ScraperAuthResult
}

export async function testScraperAuth(): Promise<ScraperAuthStatus> {
  const res = await api.get('/scrape/test-auth')
  return res.data
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await api.patch('/auth/password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}
