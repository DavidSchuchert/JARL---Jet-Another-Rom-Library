import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '@/router'

function parseJwt(token: string): any {
  const base64 = token.split('.')[1]
  return JSON.parse(atob(base64))
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('jarl_token'))
  const user = ref<{ username: string } | null>(null)
  const role = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  async function login(username: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post('/api/auth/login', formData)
      token.value = response.data.access_token
      localStorage.setItem('jarl_token', token.value!)

      // Extract role and username from JWT payload
      const payload = parseJwt(token.value!)
      role.value = payload.role ?? null
      user.value = { username: payload.sub ?? username }

      // Setup default header for subsequent requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

      router.push('/')
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    role.value = null
    localStorage.removeItem('jarl_token')
    delete axios.defaults.headers.common['Authorization']
    router.push('/login')
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      const response = await axios.get('/api/auth/me')
      role.value = response.data.role ?? null
      user.value = { username: response.data.username }
      return true
    } catch (err) {
      logout()
      return false
    }
  }

  return {
    token,
    user,
    role,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth
  }
})
