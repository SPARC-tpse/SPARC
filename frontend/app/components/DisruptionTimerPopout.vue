<!-- frontend/app/components/DisruptionTimerPopout.vue -->
<script setup lang="ts">
import { computed } from 'vue'

type Pos = { x: number; y: number }

const props = defineProps<{
  visible: boolean
  isRunning: boolean
  isPaused: boolean
  formatted: string
  pos: Pos
  onPointerDown: (e: PointerEvent) => void
  onPointerMove: (e: PointerEvent) => void
  onPointerUp: () => void
  onStart: () => void
  onPause: () => void
  onResume: () => void
  onStop: () => void
}>()

const { theme } = useAppTheme()

const primaryLabel = computed(() => {
  if (!props.isRunning && !props.isPaused) return 'Start'
  if (props.isPaused) return 'Resume'
  return 'Pause'
})

function onPrimaryClick() {
  if (!props.isRunning && !props.isPaused) {
    props.onStart()
    return
  }
  if (props.isPaused) {
    props.onResume()
    return
  }
  props.onPause()
}
</script>

<template>
  <div
    v-if="props.visible && (props.isRunning || props.isPaused)"
    :class="theme.popoutContainer"
    :style="{ left: props.pos.x + 'px', top: props.pos.y + 'px' }"
  >
    <div
      :class="theme.popoutHeader"
      @pointerdown="props.onPointerDown"
      @pointermove="props.onPointerMove"
      @pointerup="props.onPointerUp"
      @pointercancel="props.onPointerUp"
    >
      <div class="flex items-center justify-between gap-3">
        <span class="uppercase tracking-[0.12em] opacity-90">Disruption-Timer</span>

        <div class="flex items-center gap-2">
          <span
            v-if="props.isRunning"
            class="inline-flex h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse"
            aria-hidden="true"
          />
        </div>
      </div>
    </div>

    <div class="p-4 space-y-4">
      <div class="text-3xl font-mono text-center font-bold tracking-tighter">
        {{ props.formatted }}
      </div>

      <div class="flex gap-2 justify-center">
        <button
          class="rounded-lg px-3 py-2 text-sm font-semibold transition-colors
                 focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0"
          :class="(!props.isRunning && !props.isPaused)
            ? 'bg-emerald-600 text-white hover:bg-emerald-500 shadow-md'
            : theme.popoutBtnSecondary"
          @click="onPrimaryClick"
        >
          {{ primaryLabel }}
        </button>

        <button
          :class="theme.popoutBtnSecondary"
          @click="props.onStop"
          :disabled="!props.isRunning && !props.isPaused"
        >
          Stop
        </button>
      </div>
    </div>
  </div>
</template>

