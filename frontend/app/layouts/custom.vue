<script setup lang="js">
import { ref } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute} from "vue-router"
import { useDisruptionTimer } from '~/composables/useDisruptionTimer'
import { useDisruptionDraft } from '~/composables/useDisruptionDraft'

// Get theme for background color
const { isDarkMode } = useTheme()
const route = useRoute()


// Globaler Timer (läuft bei Tabwechsel weiter, weil useState)
const {
  isRunning,
  isPaused,
  formatted,
  popoutVisible,
  popoutPos,
  start,
  pause,
  resume,
  stopAndMaybeApply,
  ensureTicking,
} = useDisruptionTimer()

/**
const newDisruption = useState('disruption:newForm', () => ({
  name: '',
  start: '',
  end: '',
  resource: '',
  type: ''
}))
 */

const { draft: newDisruption } = useDisruptionDraft()

// Drag&Drop (Pointer Events)
const dragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const onPointerDown = (e) => {
  dragging.value = true
  dragOffset.value = { x: e.clientX - popoutPos.value.x, y: e.clientY - popoutPos.value.y }
  e.currentTarget?.setPointerCapture?.(e.pointerId)
}

const onPointerMove = (e) => {
  if (!dragging.value) return
  popoutPos.value = { x: e.clientX - dragOffset.value.x, y: e.clientY - dragOffset.value.y }
}

const onPointerUp = () => {
  dragging.value = false
}

// Popout beim Tabwechsel einblenden (aber nur wenn Timer läuft oder pausiert ist)
const handleVisibilityChange = () => {
  if (document.hidden && (isRunning.value || isPaused.value)) {
    popoutVisible.value = true
  }
}

const isDisruptionRoute = (path) => path === '/disruption' || path.startsWith('/disruption/')

// Popout ein-/ausblenden je nach Route
watch(
  () => route.path,
  (path) => {
    if (isDisruptionRoute(path)) {
      popoutVisible.value = false
      if (isRunning.value || isPaused.value) ensureTicking()
      return
    }

    if (isRunning.value || isPaused.value) {
      popoutVisible.value = true
      ensureTicking()
    } else {
      popoutVisible.value = false
    }
  },
  { immediate: true }
)

onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>


<template>
  <!-- Main container with flex layout -->
  <div class="min-h-screen flex transition-colors duration-300"
       :class="isDarkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'">

    <!-- Left side: Page content (takes up remaining space) -->
    <div class="flex-1 min-w-0">
      <!-- This is where page content gets injected -->
      <slot />
    </div>

    <!-- Right side: Navigation Sidebar (fixed width) -->
    <Navbar />

  </div>

  <!-- Popout Timer (liegt außerhalb des Flex-Containers, fixed im Viewport) -->
  <div
    v-if="popoutVisible && (isRunning || isPaused)"
    class="fixed z-50 w-64 rounded-lg border border-slate-300 bg-white text-slate-900 shadow-lg select-none"
    :style="{ left: popoutPos.x + 'px', top: popoutPos.y + 'px' }"
  >
    <div
      class="cursor-move px-3 py-2 border-b border-slate-200 bg-slate-50 font-semibold text-sm"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      Disruption\-Timer
    </div>

    <div class="p-3 space-y-3">
      <div class="text-2xl font-mono text-center">{{ formatted }}</div>

      <div class="flex gap-2 justify-center">
        <button class="px-3 py-2 rounded border" @click="start" :disabled="isRunning">Start</button>
        <button class="px-3 py-2 rounded border" @click="isPaused ? resume() : pause()" :disabled="!isRunning">
          {{ isPaused ? 'Weiter' : 'Pause' }}
        </button>
        <button
            class="px-3 py-2 rounded border"
            @click="stopAndMaybeApply(newDisruption)"
            :disabled="!isRunning && !isPaused">
          Stopp
        </button>
      </div>
    </div>
  </div>
</template>