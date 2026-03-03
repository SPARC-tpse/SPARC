<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import type { WidgetLayout } from '~/composables/useDashboardLayout'

const props = defineProps<{
  widgets: WidgetLayout[]
  editMode: boolean
}>()

const emit = defineEmits<{
  (e: 'update', id: string, patch: Partial<Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>>): void
  (e: 'remove', id: string): void
}>()

const COLS = 12
const ROW_HEIGHT = 100  // px
const GAP = 8           // px

const containerRef = ref<HTMLElement>()
const containerWidth = ref(1200)
const colWidth = computed(() => (containerWidth.value - GAP * (COLS - 1)) / COLS)

// Drag state
interface DragState {
  id: string
  startMouseX: number
  startMouseY: number
  startX: number
  startY: number
  ghostX: number
  ghostY: number
  w: number
  h: number
}

// Resize state
interface ResizeState {
  id: string
  startMouseX: number
  startMouseY: number
  startW: number
  startH: number
  ghostW: number
  ghostH: number
}

const dragging = ref<DragState | null>(null)
const resizing = ref<ResizeState | null>(null)

const gridHeight = computed(() => {
  const maxRow = props.widgets.reduce((m, w) => Math.max(m, w.y + w.h), 0)
  const extra = (dragging.value || resizing.value) ? 4 : 1
  return (maxRow + extra) * (ROW_HEIGHT + GAP)
})

function widgetStyle(w: WidgetLayout) {
  const isDragging = dragging.value?.id === w.id
  const isResizing = resizing.value?.id === w.id

  let x = w.x, y = w.y, ww = w.w, hh = w.h
  if (isDragging && dragging.value) {
    x = dragging.value.ghostX
    y = dragging.value.ghostY
  }
  if (isResizing && resizing.value) {
    ww = resizing.value.ghostW
    hh = resizing.value.ghostH
  }

  return {
    position: 'absolute' as const,
    left:   `${x * (colWidth.value + GAP)}px`,
    top:    `${y * (ROW_HEIGHT + GAP)}px`,
    width:  `${ww * colWidth.value + (ww - 1) * GAP}px`,
    height: `${hh * ROW_HEIGHT + (hh - 1) * GAP}px`,
    zIndex: (isDragging || isResizing) ? 100 : 1,
    transition: (isDragging || isResizing) ? 'none' : 'left 0.2s, top 0.2s, width 0.2s, height 0.2s',
  }
}

function ghostStyle() {
  if (!dragging.value) return {}
  const { ghostX, ghostY, w, h } = dragging.value
  return {
    position:   'absolute' as const,
    left:        `${ghostX * (colWidth.value + GAP)}px`,
    top:         `${ghostY * (ROW_HEIGHT + GAP)}px`,
    width:       `${w  * colWidth.value + (w  - 1) * GAP}px`,
    height:      `${h  * ROW_HEIGHT    + (h  - 1) * GAP}px`,
    background: 'rgba(245,158,11,0.12)',
    border:     '2px dashed rgba(245,158,11,0.5)',
    borderRadius: '6px',
    zIndex:      0,
    pointerEvents: 'none' as const,
  }
}

// ── Drag ──────────────────────────────────────────────────────────────────────
function startDrag(e: MouseEvent, widget: WidgetLayout) {
  if (!props.editMode) return
  e.preventDefault()
  dragging.value = {
    id: widget.id,
    startMouseX: e.clientX,
    startMouseY: e.clientY,
    startX: widget.x,
    startY: widget.y,
    ghostX: widget.x,
    ghostY: widget.y,
    w: widget.w,
    h: widget.h,
  }
}

function onMouseMove(e: MouseEvent) {
  if (dragging.value) {
    const dx = e.clientX - dragging.value.startMouseX
    const dy = e.clientY - dragging.value.startMouseY
    const rawX = dragging.value.startX + dx / (colWidth.value + GAP)
    const rawY = dragging.value.startY + dy / (ROW_HEIGHT + GAP)
    dragging.value.ghostX = Math.max(0, Math.min(COLS - dragging.value.w, Math.round(rawX)))
    dragging.value.ghostY = Math.max(0, Math.round(rawY))
  }

  if (resizing.value) {
    const dx = e.clientX - resizing.value.startMouseX
    const dy = e.clientY - resizing.value.startMouseY
    const rawW = resizing.value.startW + dx / (colWidth.value + GAP)
    const rawH = resizing.value.startH + dy / (ROW_HEIGHT + GAP)
    const widget = props.widgets.find(w => w.id === resizing.value!.id)!
    resizing.value.ghostW = Math.max(1, Math.min(COLS - widget.x, Math.round(rawW)))
    resizing.value.ghostH = Math.max(1, Math.round(rawH))
  }
}

function onMouseUp() {
  if (dragging.value) {
    emit('update', dragging.value.id, { x: dragging.value.ghostX, y: dragging.value.ghostY })
    dragging.value = null
  }
  if (resizing.value) {
    emit('update', resizing.value.id, { w: resizing.value.ghostW, h: resizing.value.ghostH })
    resizing.value = null
  }
}

// ── Resize ────────────────────────────────────────────────────────────────────
function startResize(e: MouseEvent, widget: WidgetLayout) {
  if (!props.editMode) return
  e.preventDefault()
  e.stopPropagation()
  resizing.value = {
    id: widget.id,
    startMouseX: e.clientX,
    startMouseY: e.clientY,
    startW: widget.w,
    startH: widget.h,
    ghostW: widget.w,
    ghostH: widget.h,
  }
}

// ── ResizeObserver ────────────────────────────────────────────────────────────
let ro: ResizeObserver | null = null
onMounted(async () => {
  await nextTick()
  if (containerRef.value) {
    containerWidth.value = containerRef.value.clientWidth
    ro = new ResizeObserver(entries => {
      containerWidth.value = entries[0].contentRect.width
    })
    ro.observe(containerRef.value)
  }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})
onUnmounted(() => {
  ro?.disconnect()
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<template>
  <div
    ref="containerRef"
    class="grid-container"
    :class="{ 'edit-active': editMode }"
    :style="{ height: `${gridHeight}px` }"
  >
    <!-- Drop ghost -->
    <div v-if="dragging" :style="ghostStyle()" class="drop-ghost" />

    <!-- Widgets -->
    <div
      v-for="widget in widgets"
      :key="widget.id"
      :style="widgetStyle(widget)"
      class="grid-item"
      :class="{
        'is-dragging': dragging?.id === widget.id,
        'is-resizing': resizing?.id === widget.id,
      }"
    >
      <!-- Drag handle (edit mode only) -->
      <div
        v-if="editMode"
        class="drag-handle"
        @mousedown="startDrag($event, widget)"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="handle-icon">
          <circle cx="7" cy="5" r="1.5" /><circle cx="13" cy="5" r="1.5" />
          <circle cx="7" cy="10" r="1.5" /><circle cx="13" cy="10" r="1.5" />
          <circle cx="7" cy="15" r="1.5" /><circle cx="13" cy="15" r="1.5" />
        </svg>
      </div>

      <!-- Widget slot -->
      <slot :widget="widget" :edit-mode="editMode" />

      <!-- Resize handle (edit mode only) -->
      <div
        v-if="editMode"
        class="resize-handle"
        @mousedown="startResize($event, widget)"
      >
        <svg viewBox="0 0 16 16" fill="currentColor" class="resize-icon">
          <path d="M6 14l8-8v8H6zm2 0h6v-6l-6 6z"/>
        </svg>
      </div>
    </div>

    <!-- Edit-mode grid lines overlay -->
    <div v-if="editMode" class="grid-lines" aria-hidden="true">
      <div
        v-for="c in COLS"
        :key="c"
        class="grid-col-line"
        :style="{ left: `${(c - 1) * (colWidth + GAP)}px`, width: `${colWidth}px` }"
      />
    </div>
  </div>
</template>

<style scoped>
.grid-container {
  position: relative;
  width: 100%;
  user-select: none;
}

.grid-item {
  position: absolute;
  border-radius: 8px;
  overflow: hidden;
}
.grid-item.is-dragging {
  opacity: 0.85;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  cursor: grabbing;
}
.grid-item.is-resizing {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.drag-handle {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  cursor: grab;
  color: rgba(255,255,255,0.3);
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255,255,255,0.05);
  transition: color 0.15s, background 0.15s;
}
.drag-handle:hover {
  color: #f59e0b;
  background: rgba(245,158,11,0.15);
}
.drag-handle:active { cursor: grabbing; }
.handle-icon { width: 16px; height: 16px; }

.resize-handle {
  position: absolute;
  bottom: 4px;
  right: 4px;
  z-index: 10;
  cursor: se-resize;
  color: rgba(255,255,255,0.2);
  padding: 3px;
  border-radius: 3px;
  transition: color 0.15s;
}
.resize-handle:hover { color: #f59e0b; }
.resize-icon { width: 14px; height: 14px; }

.drop-ghost {
  border-radius: 8px;
  transition: none;
}

.grid-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.grid-col-line {
  position: absolute;
  top: 0;
  bottom: 0;
  background: rgba(245, 158, 11, 0.04);
  border: 1px dashed rgba(245, 158, 11, 0.12);
  border-radius: 4px;
}
</style>
