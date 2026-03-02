<script setup lang="js">
import { computed } from 'vue'
import { useDisruptionDraft} from "~/composables/useDisruptionDraft.ts";
import { useOrderDraft } from '~/composables/useOrderDraft'
import { useResourceDraft } from '~/composables/useResourceDraft'
import { useWorkerDraft } from '~/composables/useWorkerDraft'
import { useZoom } from '~/composables/useZoom';

const { theme, isDarkMode } = useAppTheme()
const route = useRoute()
const { zoomIn, zoomOut, resetZoom, zoomPercent } = useZoom();

// Hilfsfunktion für den aktiven Pfad
const isActive = (path) => route.path.startsWith(path)

// Zentralisierte Navigations-Links
const navLinks = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Orders', path: '/order' },
  { name: 'Disruptions', path: '/disruption' },
  { name: 'Resources', path: '/resource' },
  { name: 'Workers', path: '/worker' }
]

const { draft: disruptionDraft } = useDisruptionDraft()
const {isRunning, isPaused} = useDisruptionTimer()

const hasOpenDisruptionDraft = computed(() => {
  if (isRunning.value || isPaused.value) return true
  const d = disruptionDraft.value
  return Boolean(d && ((d.name && String(d.name).trim()) || d.resource || d.start || d.end || d.type))
})

const { draft: orderDraft } = useOrderDraft()
const hasOpenOrderDraft = computed(() => {
  const d = orderDraft.value
  return Boolean(d && ((d.name && String(d.name).trim()) || d.start || d.end || d.target || d.product))
})

const { draft: resourceDraft } = useResourceDraft()
const hasOpenResourceDraft = computed(() => {
  const d = resourceDraft.value
  return Boolean(d && (d.name && String(d.name).trim()))
})

const { draft: workerDraft } = useWorkerDraft()
const hasOpenWorkerDraft = computed(() => {
  const d = workerDraft.value
  return Boolean(d && (d.name && String(d.name).trim()))
})

function toForLink(link) {
  if (link.path === '/dashboard') return link.path

  // Bei offenem Draft direkt auf /new
  if (link.path === '/disruption') return hasOpenDisruptionDraft.value ? '/disruption/new' : '/disruption/overview'
  if (link.path === '/order') return hasOpenOrderDraft.value ? '/order/new' : '/order/overview'
  if (link.path === '/resource') return hasOpenResourceDraft.value ? '/resource/new' : '/resource/overview'
  if (link.path === '/worker') return hasOpenWorkerDraft.value ? '/worker/new' : '/worker/overview'


  // Default für alle anderen
  return `${link.path}/overview`
}

</script>

<template>
  <aside :class="theme.sidebar">
    
    <h2 :class="theme.navLabel">
      Navigation
    </h2>

    <nav class="flex flex-col gap-2 flex-1">
      <NuxtLink
        v-for="link in navLinks"
        :key="link.path"
        :to="toForLink(link)"
        :class="isActive(link.path) ? theme.navLinkActive : theme.navLinkInactive"
      >
        {{ link.name }}
      </NuxtLink>
    </nav>

    <div :class="theme.navFooter" class="mt-auto">
      <div class="flex items-center gap-2">
        <div :class="theme.modeIndicator"></div>
        <span>Mode: {{ isDarkMode ? 'Dark' : 'Light' }}</span>
      </div>

      <div class="mt-3 pt-3 border-t border-slate-200/60 flex items-center gap-2">
        <button
          type="button"
          :class="theme.zoomBtn"
          @click="zoomOut"
          aria-label="Zoom verkleinern"
        >
          -
        </button>

        <span :class="[theme.zoomBtn, 'border-none min-w-14 text-center tabular-nums text-sm']">
          {{ zoomPercent }}
        </span>

        <button
          type="button"
          :class="theme.zoomBtn"
          @click="zoomIn"
          aria-label="Zoom vergrößern"
        >
          +
        </button>

        <button
          type="button"
          :class="[theme.zoomBtn, 'ml-auto text-sm']"
          @click="resetZoom"
        >
          Reset
        </button>
      </div>
    </div>
  </aside>
</template>