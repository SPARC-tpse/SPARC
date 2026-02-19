<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed, provide } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute} from "vue-router"

import Navbar from "~/components/Navbar.vue";
import Topbar from "~/components/Topbar.vue";
import DisruptionTimerPopout from "~/components/DisruptionTimerPopout.vue";

import { useDisruptionTimer } from '~/composables/useDisruptionTimer'
import { useDisruptionDraft } from '~/composables/useDisruptionDraft'


// Get theme for background color
const { isDarkMode } = useTheme()
const route = useRoute()

type TopbarActions = {
  reset?: () => void | Promise<void>
  submit?: () => void | Promise<void>
  canSubmit?: { value: boolean } | (() => boolean)
}

// Layout-Props kommen pro Page über definePageMeta({ layoutProps: {...} })
const layoutProps = computed(() => (route.meta?.layoutProps ?? {}) as Record<string, any>)

const title = computed(() => layoutProps.value.title ?? '')
const showReset = computed(() => layoutProps.value.showReset ?? true)
const showCreate = computed(() => layoutProps.value.showCreate ?? true)
const createLabel = computed(() => layoutProps.value.createLabel ?? 'Create')

// Registry: page registriert Reset/Submit + reaktives canSubmit
const actionsRef = shallowRef<Required<TopbarActions>>({
  reset: undefined,
  submit: undefined,
  canSubmit: undefined,
})

function registerTopbarActions(next: TopbarActions = {}) {
  actionsRef.value = {
    reset: typeof next.reset === 'function' ? next.reset : undefined,
    submit: typeof next.submit === 'function' ? next.submit : undefined,
    canSubmit:
      typeof next.canSubmit === 'function' || (next.canSubmit && typeof (next.canSubmit as any).value === 'boolean')
        ? next.canSubmit
        : undefined,
  }
}

// Für Pages verfügbar machen
provide('registerTopbarActions', registerTopbarActions)

// Auflösen, ob Submit erlaubt ist (reactive über ref oder function)
const canSubmit = computed(() => {
  const src = actionsRef.value.canSubmit
  if (!src) return false
  if (typeof src === 'function') return Boolean(src())
  return Boolean(src.value)
})

async function handleReset() {
  await actionsRef.value.reset?.()
}

async function handleSubmit() {
  if (!canSubmit.value) return
  await actionsRef.value.submit?.()
}

const topbarTitle = computed(() => {
  // Page-spezifischer Titel (falls gesetzt)
  const fromMeta = layoutProps.value?.title
  if (typeof fromMeta === 'string' && fromMeta.trim().length) return fromMeta
  // Fallback anhand der Route
  const p = route.path
  if (p.startsWith('/dashboard')) return 'Dashboard'
  if (p.startsWith('/order')) return 'Orders'
  if (p.startsWith('/disruption')) return 'Disruptions'
  if (p.startsWith('/resource')) return 'Resources'
  if (p.startsWith('/worker')) return 'Workers'
  return 'Home'
})



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

/*
const topbarTitle = computed(() => {
  const p = route.path;
  if (p.startsWith("/dashboard")) return "Dashboard";
  if (p.startsWith("/order")) return "Orders";
  if (p.startsWith("/disruption")) return "Disruptions";
  if (p.startsWith("/resource")) return "Resources";
  if (p.startsWith("/worker")) return "Workers";
  return "Home";
});
 */


</script>


<template>
  <!-- Main container with flex layout -->
  <div class="h-screen overflow-hidden flex transition-colors duration-300"
       :class="isDarkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'">


    <!-- Left side: Page content (takes up remaining space) -->
    <div class="flex-1 min-w-0 flex flex-col min-h-0">
      <Topbar
        v-if="title"
        :title="title"
        :show-reset="showReset"
        :show-create="showCreate"
        :create-label="createLabel"
        :can-submit="canSubmit"
        @reset="handleReset"
        @submit="handleSubmit"
      />
      <!-- This is where page content gets injected -->
      <div class="flex-1 min-h-0 overflow-auto">
        <div class="zoom-root">
          <slot />
        </div>
      </div>
    </div>

    <!-- Right side: Navigation Sidebar (fixed width, NOT zoomed) -->
    <Navbar class="h-full" />
  </div>

   <!-- Popout Timer (liegt außerhalb des Flex-Containers, fixed im Viewport) -->
  <div
    v-if="popoutVisible && (isRunning || isPaused)"
    class="fixed z-50 w-64 rounded-lg border border-slate-300 bg-white text-slate-900 shadow-lg select-none"
    :style="{ left: popoutPos.x + 'px', top: popoutPos.y + 'px' }"
  >
    <DisruptionTimerPopout
      :visible="popoutVisible"
      :is-running="isRunning"
      :is-paused="isPaused"
      :formatted="formatted"
      :pos="popoutPos"
      :on-pointer-down="onPointerDown"
      :on-pointer-move="onPointerMove"
      :on-pointer-up="onPointerUp"
      :on-start="start"
      :on-pause="pause"
      :on-resume="resume"
      :on-stop="() => stopAndMaybeApply(newDisruption)"
    />

    <!--
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
    -->
  </div>

</template>

<style scoped>
.zoom-root {
  transform: scale(var(--app-zoom, 1));
  transform-origin: top left;
  width: calc(100% / var(--app-zoom, 1));
  height: calc(100% / var(--app-zoom, 1));
}
</style>