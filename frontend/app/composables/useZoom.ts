// frontend/app/composables/useZoom.ts
import { computed, onMounted, ref, watch } from "vue";

const STORAGE_KEY = "sparc:zoom";
const DEFAULT_ZOOM = 1.0;
const MIN_ZOOM = 0.75;
const MAX_ZOOM = 1.5;
const STEP = 0.1;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function roundToOneDecimal(value: number): number {
  return Math.round(value * 10) / 10;
}

function applyZoomCssVariable(zoom: number): void {
  if (typeof document === "undefined") return;
  document.documentElement.style.setProperty("--app-zoom", String(zoom));
}

export function useZoom() {
  const zoom = ref<number>(DEFAULT_ZOOM);

  const zoomPercent = computed(() => `${Math.round(zoom.value * 100)}%`);

  function setZoom(next: number): void {
    const clamped = clamp(roundToOneDecimal(next), MIN_ZOOM, MAX_ZOOM);
    zoom.value = clamped;
  }

  function zoomIn(): void {
    setZoom(zoom.value + STEP);
  }

  function zoomOut(): void {
    setZoom(zoom.value - STEP);
  }

  function resetZoom(): void {
    setZoom(DEFAULT_ZOOM);
  }

  onMounted(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = Number(raw);
        if (!Number.isNaN(parsed)) setZoom(parsed);
      }
    } catch {
      // ignore
    }
    applyZoomCssVariable(zoom.value);
  });

  watch(zoom, (val) => {
    applyZoomCssVariable(val);
    try {
      localStorage.setItem(STORAGE_KEY, String(val));
    } catch {
      // ignore
    }
  });

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
  };
}
