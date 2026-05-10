import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getRoms, deleteRom as apiDeleteRom, type Rom, type GetRomsParams } from '@/api/roms'
import { getPlatforms, type Platform } from '@/api/platforms'

export const useRomsStore = defineStore('roms', () => {
  const roms = ref<Rom[]>([])
  const platforms = ref<Platform[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const pagination = ref({
    page: 1,
    pageSize: 24,
    total: 0,
    totalPages: 0
  })

  const sort = ref<{ by: string; dir: 'asc' | 'desc' }>({ by: 'title', dir: 'asc' })

  const hasMore = computed(() => pagination.value.page < pagination.value.totalPages)

  const fetchRoms = async (params: GetRomsParams = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await getRoms({
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        sort_by: sort.value.by as GetRomsParams['sort_by'],
        sort_dir: sort.value.dir,
        ...params
      })
      roms.value = response.items
      pagination.value = {
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        totalPages: response.total_pages
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch ROMs'
      console.error('Failed to fetch ROMs:', e)
    } finally {
      loading.value = false
    }
  }

  const fetchPlatforms = async () => {
    try {
      platforms.value = await getPlatforms()
    } catch (e) {
      console.error('Failed to fetch platforms:', e)
    }
  }

  const deleteRom = async (id: number) => {
    try {
      await apiDeleteRom(id)
      roms.value = roms.value.filter(rom => rom.id !== id)
      pagination.value.total -= 1
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete ROM'
      throw e
    }
  }

  const setPage = (page: number) => {
    pagination.value.page = page
  }

  const setSort = (by: string, dir: 'asc' | 'desc') => { sort.value = { by, dir } }

  const nextPage = () => {
    if (hasMore.value) {
      pagination.value.page++
    }
  }

  const prevPage = () => {
    if (pagination.value.page > 1) {
      pagination.value.page--
    }
  }

  return {
    roms,
    platforms,
    loading,
    error,
    pagination,
    sort,
    hasMore,
    fetchRoms,
    fetchPlatforms,
    deleteRom,
    setPage,
    setSort,
    nextPage,
    prevPage
  }
})
