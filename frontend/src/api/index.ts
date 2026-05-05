import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 401:
          console.error('Unauthorized access')
          break
        case 403:
          console.error('Forbidden access')
          break
        case 404:
          console.error('Resource not found')
          break
        case 500:
          console.error('Server error')
          break
        default:
          console.error(`API Error: ${status}`)
      }
    } else if (error.request) {
      console.error('Network error - no response received')
    } else {
      console.error('Request error', error.message)
    }
    return Promise.reject(error)
  }
)

export default api
