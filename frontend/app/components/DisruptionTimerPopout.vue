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

const primaryLabel = computed(() => {
  if (!props.isRunning && !props.isPaused) return 'Start'
  if (props.isPaused) return 'Weiter'
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
    class="fixed z-50 w-64 rounded-lg border border-slate-300 bg-white text-slate-900 shadow-lg select-none"
    :style="{ left: props.pos.x + 'px', top: props.pos.y + 'px' }"
  >
    <div
      class="cursor-move px-3 py-2 border-b border-slate-200 bg-slate-50 font-semibold text-sm"
      @pointerdown="props.onPointerDown"
      @pointermove="props.onPointerMove"
      @pointerup="props.onPointerUp"
      @pointercancel="props.onPointerUp"
    >
      Disruption-Timer
    </div>

    <div class="p-3 space-y-3">
      <div class="text-2xl font-mono text-center">{{ props.formatted }}</div>

      <div class="flex gap-2 justify-center">
        <button class="px-3 py-2 rounded border" @click="onPrimaryClick">
          {{ primaryLabel }}
        </button>

        <button
          class="px-3 py-2 rounded border"
          @click="props.onStop"
          :disabled="!props.isRunning && !props.isPaused"
        >
          Stopp
        </button>
      </div>
    </div>
  </div>
</template>
