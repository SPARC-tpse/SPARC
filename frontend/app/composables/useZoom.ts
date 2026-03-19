import { computed, onMounted, ref, watch } from 'vue'

const STORAGE_KEY = 'sparc:zoom'
const DEFAULT_ZOOM = 1.0
const MIN_ZOOM = 0.75
const MAX_ZOOM = 1.5
const STEP = 0.1

const zoom = ref<number>(DEFAULT_ZOOM)
const zoomPercent = computed(() => `${Math.round(zoom.value * 100)}%`)

let initialized = false
let syncAttached = false

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

function roundToOneDecimal(value: number): number {
  return Math.round(value * 10) / 10
}

function applyZoomCssVariable(value: number): void {
  if (typeof document === 'undefined') return
  document.documentElement.style.setProperty('--app-zoom', String(value))
}

function initializeZoom(): void {
  if (initialized || typeof window === 'undefined') return

  initialized = true

  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = Number(raw)
      if (!Number.isNaN(parsed)) {
        zoom.value = clamp(roundToOneDecimal(parsed), MIN_ZOOM, MAX_ZOOM)
      }
    }
  } catch {
    // ignore localStorage read errors
  }

  applyZoomCssVariable(zoom.value)
}

function attachSync(): void {
  if (syncAttached) return

  syncAttached = true
  watch(zoom, value => {
    applyZoomCssVariable(value)
    try {
      localStorage.setItem(STORAGE_KEY, String(value))
    } catch {
      // ignore localStorage write errors
    }
  })
}

export function useZoom() {
  function setZoom(next: number): void {
    zoom.value = clamp(roundToOneDecimal(next), MIN_ZOOM, MAX_ZOOM)
  }

  function zoomIn(): void {
    setZoom(zoom.value + STEP)
  }

  function zoomOut(): void {
    setZoom(zoom.value - STEP)
  }

  function resetZoom(): void {
    setZoom(DEFAULT_ZOOM)
  }

  onMounted(() => {
    initializeZoom()
    attachSync()
    applyZoomCssVariable(zoom.value)
  })

  return {
    zoom,
    zoomPercent,
    zoomIn,
    zoomOut,
    resetZoom,
    setZoom,
    MIN_ZOOM,
    MAX_ZOOM,
    STEP,
  }
}
