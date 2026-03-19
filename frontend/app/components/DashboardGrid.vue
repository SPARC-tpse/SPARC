<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import type { WidgetLayout } from '~/composables/useDashboardLayout'

const props = defineProps<{
  widgets: WidgetLayout[]
  editMode: boolean
}>()

const emit = defineEmits<{
  (e: 'update', id: string, patch: Partial<Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>>): void
  (e: 'remove', id: string): void
}>()

const DESKTOP_COLS = 12
const TABLET_COLS = 2
const STACKED_COLS = 1
const STACKED_BREAKPOINT = 620
const TABLET_BREAKPOINT = 1080
const ROW_HEIGHT = 100
const GAP = 8

type LayoutMode = 'desktop' | 'tablet' | 'stacked'

const containerRef = ref<HTMLElement>()
const containerWidth = ref(1200)

const layoutMode = computed<LayoutMode>(() => {
  if (containerWidth.value <= STACKED_BREAKPOINT) return 'stacked'
  if (containerWidth.value <= TABLET_BREAKPOINT) return 'tablet'
  return 'desktop'
})

const gridCols = computed(() => {
  if (layoutMode.value === 'stacked') return STACKED_COLS
  if (layoutMode.value === 'tablet') return TABLET_COLS
  return DESKTOP_COLS
})

const isCompactLayout = computed(() => layoutMode.value !== 'desktop')
const canEditLayout = computed(() => props.editMode && !isCompactLayout.value)
const colWidth = computed(() => (containerWidth.value - GAP * (gridCols.value - 1)) / gridCols.value)

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

function overlaps(a: Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>, b: Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>) {
  return (
    a.x < b.x + b.w &&
    a.x + a.w > b.x &&
    a.y < b.y + b.h &&
    a.y + a.h > b.y
  )
}

function widgetOrder(a: WidgetLayout, b: WidgetLayout) {
  return a.y - b.y || a.x - b.x || a.id.localeCompare(b.id)
}

function compactSpan(widget: WidgetLayout, cols: number) {
  if (cols === 1) return 1
  if (widget.type.startsWith('gantt-') || widget.w >= 7 || widget.h >= 5) return cols
  return 1
}

function compactHeight(widget: WidgetLayout, cols: number) {
  if (cols === 1 && widget.type === 'kpi') return Math.max(2, widget.h)
  if (cols === 2 && widget.type.startsWith('gantt-')) return Math.max(4, widget.h)
  return widget.h
}

function canPlaceCompact(occupied: boolean[][], x: number, y: number, w: number, h: number, cols: number) {
  if (x + w > cols) return false

  for (let row = y; row < y + h; row += 1) {
    if (!occupied[row]) occupied[row] = Array(cols).fill(false)
    for (let col = x; col < x + w; col += 1) {
      if (occupied[row][col]) return false
    }
  }

  return true
}

function occupyCompact(occupied: boolean[][], x: number, y: number, w: number, h: number, cols: number) {
  for (let row = y; row < y + h; row += 1) {
    if (!occupied[row]) occupied[row] = Array(cols).fill(false)
    for (let col = x; col < x + w; col += 1) {
      occupied[row][col] = true
    }
  }
}

function buildCompactLayout(widgets: WidgetLayout[], cols: number) {
  const occupied: boolean[][] = []

  return [...widgets]
    .sort(widgetOrder)
    .map(widget => {
      const w = compactSpan(widget, cols)
      const h = compactHeight(widget, cols)

      let y = 0
      while (true) {
        for (let x = 0; x <= cols - w; x += 1) {
          if (!canPlaceCompact(occupied, x, y, w, h, cols)) continue

          occupyCompact(occupied, x, y, w, h, cols)
          return {
            ...widget,
            x,
            y,
            w,
            h,
          }
        }
        y += 1
      }
    })
}

const renderedWidgets = computed(() => {
  if (!isCompactLayout.value) return props.widgets
  return buildCompactLayout(props.widgets, gridCols.value)
})

const gridHeight = computed(() => {
  const maxRow = renderedWidgets.value.reduce((max, widget) => Math.max(max, widget.y + widget.h), 0)
  const extra = dragging.value || resizing.value ? 4 : 1
  return (maxRow + extra) * (ROW_HEIGHT + GAP)
})

const dropTargetId = computed(() => {
  if (!dragging.value || !canEditLayout.value) return null

  const dragRect = {
    x: dragging.value.ghostX,
    y: dragging.value.ghostY,
    w: dragging.value.w,
    h: dragging.value.h,
  }
  const collisions = renderedWidgets.value.filter(widget => widget.id !== dragging.value?.id && overlaps(dragRect, widget))

  return collisions.length === 1 ? collisions[0].id : null
})

function widgetStyle(widget: WidgetLayout) {
  const isDragging = dragging.value?.id === widget.id
  const isResizing = resizing.value?.id === widget.id

  let x = widget.x
  let y = widget.y
  let w = widget.w
  let h = widget.h

  if (isDragging && dragging.value) {
    x = dragging.value.ghostX
    y = dragging.value.ghostY
  }

  if (isResizing && resizing.value) {
    w = resizing.value.ghostW
    h = resizing.value.ghostH
  }

  return {
    position: 'absolute' as const,
    left: `${x * (colWidth.value + GAP)}px`,
    top: `${y * (ROW_HEIGHT + GAP)}px`,
    width: `${w * colWidth.value + (w - 1) * GAP}px`,
    height: `${h * ROW_HEIGHT + (h - 1) * GAP}px`,
    zIndex: isDragging || isResizing ? 100 : 1,
    transition: isDragging || isResizing ? 'none' : 'left 0.2s ease, top 0.2s ease, width 0.2s ease, height 0.2s ease',
  }
}

function ghostStyle() {
  if (!dragging.value) return {}

  return {
    position: 'absolute' as const,
    left: `${dragging.value.ghostX * (colWidth.value + GAP)}px`,
    top: `${dragging.value.ghostY * (ROW_HEIGHT + GAP)}px`,
    width: `${dragging.value.w * colWidth.value + (dragging.value.w - 1) * GAP}px`,
    height: `${dragging.value.h * ROW_HEIGHT + (dragging.value.h - 1) * GAP}px`,
    background: 'var(--dashboard-ghost-bg)',
    border: '2px dashed var(--dashboard-ghost-border)',
    borderRadius: '8px',
    zIndex: 0,
    pointerEvents: 'none' as const,
  }
}

function startDrag(event: MouseEvent, widget: WidgetLayout) {
  if (!canEditLayout.value) return

  event.preventDefault()
  dragging.value = {
    id: widget.id,
    startMouseX: event.clientX,
    startMouseY: event.clientY,
    startX: widget.x,
    startY: widget.y,
    ghostX: widget.x,
    ghostY: widget.y,
    w: widget.w,
    h: widget.h,
  }
}

function startResize(event: MouseEvent, widget: WidgetLayout) {
  if (!canEditLayout.value) return

  event.preventDefault()
  event.stopPropagation()
  resizing.value = {
    id: widget.id,
    startMouseX: event.clientX,
    startMouseY: event.clientY,
    startW: widget.w,
    startH: widget.h,
    ghostW: widget.w,
    ghostH: widget.h,
  }
}

function onMouseMove(event: MouseEvent) {
  if (dragging.value) {
    const dx = event.clientX - dragging.value.startMouseX
    const dy = event.clientY - dragging.value.startMouseY
    const rawX = dragging.value.startX + dx / (colWidth.value + GAP)
    const rawY = dragging.value.startY + dy / (ROW_HEIGHT + GAP)

    dragging.value.ghostX = Math.max(0, Math.min(DESKTOP_COLS - dragging.value.w, Math.round(rawX)))
    dragging.value.ghostY = Math.max(0, Math.round(rawY))
  }

  if (resizing.value) {
    const dx = event.clientX - resizing.value.startMouseX
    const dy = event.clientY - resizing.value.startMouseY
    const rawW = resizing.value.startW + dx / (colWidth.value + GAP)
    const rawH = resizing.value.startH + dy / (ROW_HEIGHT + GAP)
    const widget = props.widgets.find(item => item.id === resizing.value?.id)

    if (!widget) return

    resizing.value.ghostW = Math.max(1, Math.min(DESKTOP_COLS - widget.x, Math.round(rawW)))
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

let resizeObserver: ResizeObserver | null = null

onMounted(async () => {
  await nextTick()

  if (containerRef.value) {
    containerWidth.value = containerRef.value.clientWidth
    resizeObserver = new ResizeObserver(entries => {
      containerWidth.value = entries[0].contentRect.width
    })
    resizeObserver.observe(containerRef.value)
  }

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<template>
  <div
    ref="containerRef"
    class="grid-container"
    :class="{
      'edit-active': canEditLayout,
      'grid-container--compact': isCompactLayout,
      'grid-container--stacked': layoutMode === 'stacked',
    }"
    :style="{ height: `${gridHeight}px` }"
  >
    <div v-if="dragging" :style="ghostStyle()" class="drop-ghost" />

    <div
      v-for="widget in renderedWidgets"
      :key="widget.id"
      :style="widgetStyle(widget)"
      class="grid-item"
      :class="{
        'is-dragging': dragging?.id === widget.id,
        'is-resizing': resizing?.id === widget.id,
        'is-drop-target': dropTargetId === widget.id,
      }"
    >
      <div
        v-if="canEditLayout"
        class="drag-handle"
        @mousedown="startDrag($event, widget)"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="handle-icon">
          <circle cx="7" cy="5" r="1.5" />
          <circle cx="13" cy="5" r="1.5" />
          <circle cx="7" cy="10" r="1.5" />
          <circle cx="13" cy="10" r="1.5" />
          <circle cx="7" cy="15" r="1.5" />
          <circle cx="13" cy="15" r="1.5" />
        </svg>
      </div>

      <slot :widget="widget" :edit-mode="props.editMode" />

      <div
        v-if="canEditLayout"
        class="resize-handle"
        @mousedown="startResize($event, widget)"
      >
        <svg viewBox="0 0 16 16" fill="currentColor" class="resize-icon">
          <path d="M6 14l8-8v8H6zm2 0h6v-6l-6 6z" />
        </svg>
      </div>
    </div>

    <div v-if="canEditLayout" class="grid-lines" aria-hidden="true">
      <div
        v-for="column in DESKTOP_COLS"
        :key="column"
        class="grid-col-line"
        :style="{ left: `${(column - 1) * (colWidth + GAP)}px`, width: `${colWidth}px` }"
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
  opacity: 0.88;
  box-shadow: var(--dashboard-shadow-soft);
  cursor: grabbing;
}

.grid-item.is-resizing {
  box-shadow: var(--dashboard-shadow-soft);
}

.grid-item.is-drop-target {
  box-shadow: 0 0 0 2px var(--dashboard-accent-border);
}

.drag-handle {
  position: absolute;
  top: 8px;
  left: 50%;
  z-index: 10;
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--dashboard-handle-color);
  background: var(--dashboard-handle-bg);
  cursor: grab;
  transform: translateX(-50%);
  transition: color 0.15s ease, background 0.15s ease;
}

.drag-handle:hover {
  color: var(--dashboard-accent);
  background: color-mix(in srgb, var(--dashboard-accent) 14%, transparent);
}

.drag-handle:active {
  cursor: grabbing;
}

.handle-icon {
  width: 16px;
  height: 16px;
}

.resize-handle {
  position: absolute;
  right: 4px;
  bottom: 4px;
  z-index: 10;
  padding: 3px;
  border-radius: 3px;
  color: var(--dashboard-resize-color);
  cursor: se-resize;
  transition: color 0.15s ease;
}

.resize-handle:hover {
  color: var(--dashboard-accent);
}

.resize-icon {
  width: 14px;
  height: 14px;
}

.drop-ghost {
  border-radius: 8px;
}

.grid-lines {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.grid-col-line {
  position: absolute;
  top: 0;
  bottom: 0;
  background: var(--dashboard-grid-line-bg);
  border: 1px dashed var(--dashboard-grid-line-border);
  border-radius: 4px;
}

.grid-container--compact .grid-item {
  border-radius: 10px;
}

.grid-container--stacked .grid-item {
  border-radius: 12px;
}
</style>
