import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('jarl_token'))
  const user = ref<{ username: string } | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

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
    localStorage.removeItem('jarl_token')
    delete axios.defaults.headers.common['Authorization']
    router.push('/login')
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      await axios.get('/api/auth/me')
      return true
    } catch (err) {
      logout()
      return false
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
})
