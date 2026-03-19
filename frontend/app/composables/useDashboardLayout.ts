import { computed, ref } from 'vue'

export type WidgetType =
  | 'orders'
  | 'resources'
  | 'kpi'
  | 'disruptions-chart'
  | 'gantt-order'
  | 'gantt-process'
  | 'gantt-resource'

export interface WidgetDef {
  type: WidgetType
  title: string
  defaultW: number
  defaultH: number
  redirect?: string
}

export interface WidgetLayout {
  id: string
  type: WidgetType
  title: string
  redirect?: string
  x: number
  y: number
  w: number
  h: number
  visible: boolean
}

export const WIDGET_DEFS: WidgetDef[] = [
  { type: 'orders',            title: 'Orders',             defaultW: 6, defaultH: 4 },
  { type: 'resources',         title: 'Resources',          defaultW: 4, defaultH: 4 },
  { type: 'kpi',               title: 'KPI Overview',       defaultW: 8, defaultH: 3 },
  { type: 'disruptions-chart', title: 'Disruptions',        defaultW: 5, defaultH: 4 },
  { type: 'gantt-order',       title: 'Gantt Â· Order',     defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/order' },
  { type: 'gantt-process',     title: 'Gantt Â· Process',   defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/process' },
  { type: 'gantt-resource',    title: 'Gantt Â· Resource',  defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/resource' },
]

const STORAGE_KEY = 'dashboard-layout-v1'
const COLS = 12

type GridPatch = Partial<Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>>
type GridPosition = Pick<WidgetLayout, 'x' | 'y'>

const DEFAULT_LAYOUT: WidgetLayout[] = [
  { id: 'w-kpi',         type: 'kpi',               title: 'KPI Overview',   x: 0, y: 0, w: 6,  h: 3, visible: true },
  { id: 'w-orders',      type: 'orders',            title: 'Orders',         x: 0, y: 3, w: 6,  h: 4, visible: true },
  { id: 'w-resources',   type: 'resources',         title: 'Resources',      x: 6, y: 0, w: 6,  h: 3, visible: true },
  { id: 'w-disruptions', type: 'disruptions-chart', title: 'Disruptions',    x: 6, y: 3, w: 6,  h: 4, visible: true },
  { id: 'w-gantt-order', type: 'gantt-order',       title: 'Gantt Â· Order', redirect: '/dashboard/gantt/order', x: 0, y: 7, w: 12, h: 4, visible: true },
]

function cloneLayout(layout: WidgetLayout[]) {
  return layout.map(widget => ({ ...widget }))
}

function clampWidget(widget: WidgetLayout): WidgetLayout {
  const width = Math.max(1, Math.min(COLS, widget.w))

  return {
    ...widget,
    x: Math.max(0, Math.min(COLS - width, widget.x)),
    y: Math.max(0, widget.y),
    w: width,
    h: Math.max(1, widget.h),
  }
}

function overlaps(a: Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>, b: Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>) {
  return (
    a.x < b.x + b.w &&
    a.x + a.w > b.x &&
    a.y < b.y + b.h &&
    a.y + a.h > b.y
  )
}

function canPlace(widget: WidgetLayout, occupied: WidgetLayout[]) {
  if (widget.x < 0 || widget.y < 0 || widget.x + widget.w > COLS || widget.h < 1) {
    return false
  }

  return occupied.every(other =>
    other.id === widget.id ||
    !other.visible ||
    !overlaps(widget, other)
  )
}

function buildAxisOrder(start: number, min: number, max: number) {
  const clampedStart = Math.max(min, Math.min(max, start))
  const order: number[] = []

  order.push(clampedStart)

  for (let offset = 1; order.length < max - min + 1; offset += 1) {
    const right = clampedStart + offset
    if (right <= max) order.push(right)

    const left = clampedStart - offset
    if (left >= min) order.push(left)
  }

  return order
}

function findFirstFreeSpot(widget: WidgetLayout, occupied: WidgetLayout[], preferred?: GridPosition): GridPosition {
  const startX = Math.max(0, Math.min(COLS - widget.w, preferred?.x ?? widget.x))
  const startY = Math.max(0, preferred?.y ?? widget.y)
  const maxRow = Math.max(
    startY,
    ...occupied.filter(other => other.visible).map(other => other.y + other.h),
    0,
  ) + 12

  const fitsAt = (x: number, y: number) => canPlace({ ...widget, x, y }, occupied)
  const xOrder = buildAxisOrder(startX, 0, COLS - widget.w)

  if (fitsAt(startX, startY)) {
    return { x: startX, y: startY }
  }

  for (let y = startY; y <= maxRow; y += 1) {
    for (const x of xOrder) {
      if (y === startY && x === startX) continue
      if (fitsAt(x, y)) return { x, y }
    }
  }

  for (let y = 0; y < startY; y += 1) {
    for (const x of xOrder) {
      if (fitsAt(x, y)) return { x, y }
    }
  }

  return { x: 0, y: maxRow + 1 }
}

function normalizeLayout(rawLayout: WidgetLayout[]) {
  const next = cloneLayout(rawLayout).map(clampWidget)
  const placed: WidgetLayout[] = []
  const orderedVisible = next
    .filter(widget => widget.visible)
    .sort((a, b) => a.y - b.y || a.x - b.x || a.id.localeCompare(b.id))

  for (const widget of orderedVisible) {
    if (!canPlace(widget, placed)) {
      const pos = findFirstFreeSpot(widget, placed, { x: widget.x, y: widget.y })
      widget.x = pos.x
      widget.y = pos.y
    }
    placed.push(widget)
  }

  return next
}

function resolveLayoutChange(rawLayout: WidgetLayout[], id: string, patch: GridPatch) {
  const next = cloneLayout(rawLayout)
  const target = next.find(widget => widget.id === id)
  const previous = rawLayout.find(widget => widget.id === id)

  if (!target || !previous) {
    return rawLayout
  }

  Object.assign(target, patch)
  Object.assign(target, clampWidget(target))

  if (!target.visible) {
    return next
  }

  const visibleWidgets = next.filter(widget => widget.visible)
  const collisions = visibleWidgets.filter(widget => widget.id !== target.id && overlaps(target, widget))

  if (!collisions.length) {
    return next
  }

  const collisionIds = new Set(collisions.map(widget => widget.id))
  const placed = visibleWidgets.filter(widget => widget.id !== target.id && !collisionIds.has(widget.id))
  placed.push(target)

  const sourcePosition = clampWidget({ ...previous })

  if (collisions.length === 1) {
    const displaced = collisions[0]
    const swapCandidate = clampWidget({
      ...displaced,
      x: sourcePosition.x,
      y: sourcePosition.y,
    })

    if (canPlace(swapCandidate, placed)) {
      displaced.x = swapCandidate.x
      displaced.y = swapCandidate.y
      return next
    }
  }

  const orderedCollisions = [...collisions].sort((a, b) => a.y - b.y || a.x - b.x || a.id.localeCompare(b.id))

  for (const displaced of orderedCollisions) {
    const preferred = { x: displaced.x, y: displaced.y }
    const pos = findFirstFreeSpot(displaced, placed, preferred)

    displaced.x = pos.x
    displaced.y = pos.y
    placed.push(displaced)
  }

  return next
}

function loadLayout(): WidgetLayout[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {
    // ignore malformed or unavailable storage
  }

  return JSON.parse(JSON.stringify(DEFAULT_LAYOUT))
}

function saveLayout(layout: WidgetLayout[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(layout))
  } catch {
    // ignore storage write errors
  }
}

export function useDashboardLayout() {
  const layout = ref<WidgetLayout[]>(normalizeLayout(loadLayout()))
  const editMode = ref(false)
  const addPanelOpen = ref(false)

  const visibleWidgets = computed(() => layout.value.filter(widget => widget.visible))

  function toggleEdit() {
    editMode.value = !editMode.value
    if (!editMode.value) saveLayout(layout.value)
  }

  function removeWidget(id: string) {
    const widget = layout.value.find(item => item.id === id)
    if (widget) widget.visible = false
    saveLayout(layout.value)
  }

  function addWidget(def: WidgetDef) {
    const existing = layout.value.find(widget => widget.type === def.type && !widget.visible)
    if (existing) {
      const restored = clampWidget(existing)
      const pos = findFirstFreeSpot(
        restored,
        layout.value.filter(widget => widget.visible && widget.id !== existing.id),
        { x: restored.x, y: restored.y },
      )

      Object.assign(existing, restored, pos, { visible: true })
      saveLayout(layout.value)
      return
    }

    const id = `w-${def.type}-${Date.now()}`
    const widget = clampWidget({
      id,
      type: def.type,
      title: def.title,
      redirect: def.redirect,
      x: 0,
      y: 0,
      w: def.defaultW,
      h: def.defaultH,
      visible: true,
    })
    const pos = findFirstFreeSpot(widget, layout.value.filter(item => item.visible), { x: 0, y: 0 })

    layout.value.push({
      ...widget,
      ...pos,
    })
    saveLayout(layout.value)
  }

  function updateWidget(id: string, patch: GridPatch) {
    layout.value = resolveLayoutChange(layout.value, id, patch)
  }

  function commitLayout() {
    saveLayout(layout.value)
  }

  function resetLayout() {
    layout.value = normalizeLayout(JSON.parse(JSON.stringify(DEFAULT_LAYOUT)))
    saveLayout(layout.value)
  }

  const addableWidgets = computed(() =>
    WIDGET_DEFS.filter(def => !layout.value.some(widget => widget.type === def.type && widget.visible))
  )

  return {
    layout,
    visibleWidgets,
    editMode,
    addPanelOpen,
    addableWidgets,
    toggleEdit,
    removeWidget,
    addWidget,
    updateWidget,
    commitLayout,
    resetLayout,
  }
}
