import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  startScan as apiStartScan,
  getScanStatus as apiGetScanStatus,
  getScanEvents as apiGetScanEvents,
  getCurrentScanJob as apiGetCurrentScanJob,
  type ScanEvent,
  type ScanProgress
} from '@/api/scan'

export const useScanStore = defineStore('scan', () => {
  const scanStatus = ref<ScanProgress['status']>('idle')
  const progress = ref<ScanProgress>({
    status: 'idle',
    total_files: 0,
    scanned_files: 0,
    current_file: null,
    errors: 0,
    started_at: null,
    completed_at: null
  })
  const currentJob = ref<number | null>(null)
  const scanEvents = ref<ScanEvent[]>([])
  const isPolling = ref(false)
  let pollInterval: ReturnType<typeof setInterval> | null = null
  let lastEventSequence = 0

  const startScan = async (fullScan: boolean = false) => {
    try {
      const job = await apiStartScan(fullScan)
      currentJob.value = job.id
      scanStatus.value = job.status
      progress.value = job.progress
      scanEvents.value = []
      lastEventSequence = 0
      await pollProgress()
      startPolling()
      return job
    } catch (e) {
      console.error('Failed to start scan:', e)
      throw e
    }
  }

  const pollProgress = async () => {
    if (!currentJob.value) return
    try {
      const [job, events] = await Promise.all([
        apiGetScanStatus(currentJob.value),
        apiGetScanEvents(currentJob.value, lastEventSequence)
      ])

      if (events.length > 0) {
        lastEventSequence = events[events.length - 1].sequence
        scanEvents.value = [...scanEvents.value, ...events].slice(-1000)
      }

      const eventProgress = events.reduce<Partial<ScanProgress>>((next, event) => {
        if (event.scanned_files !== null) next.scanned_files = event.scanned_files
        if (event.current_file) next.current_file = event.current_file
        return next
      }, {})

      progress.value = { ...job.progress, ...eventProgress }
      scanStatus.value = job.status
      
      if (job.status === 'completed' || job.status === 'failed') {
        stopPolling()
      }
    } catch (e) {
      console.error('Failed to poll scan progress:', e)
    }
  }

  const startPolling = () => {
    if (pollInterval) return
    isPolling.value = true
    pollInterval = setInterval(pollProgress, 1000)
  }

  const attachCurrentScan = async () => {
    const job = await apiGetCurrentScanJob()
    if (!job) return false

    currentJob.value = job.id
    progress.value = job.progress
    scanStatus.value = job.status
    scanEvents.value = []
    lastEventSequence = 0
    await pollProgress()
    startPolling()
    return true
  }

  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    isPolling.value = false
  }

  const reset = () => {
    stopPolling()
    currentJob.value = null
    scanEvents.value = []
    lastEventSequence = 0
    scanStatus.value = 'idle'
    progress.value = {
      status: 'idle',
      total_files: 0,
      scanned_files: 0,
      current_file: null,
      errors: 0,
      started_at: null,
      completed_at: null
    }
  }

  return {
    scanStatus,
    progress,
    currentJob,
    scanEvents,
    isPolling,
    startScan,
    attachCurrentScan,
    pollProgress,
    startPolling,
    stopPolling,
    reset
  }
})
