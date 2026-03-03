import { ref, computed } from 'vue'

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
  { type: 'orders',           title: 'Orders',              defaultW: 6, defaultH: 4 },
  { type: 'resources',        title: 'Resources',           defaultW: 4, defaultH: 4 },
  { type: 'kpi',              title: 'KPI Overview',        defaultW: 8, defaultH: 3 },
  { type: 'disruptions-chart',title: 'Disruptions',         defaultW: 5, defaultH: 4 },
  { type: 'gantt-order',      title: 'Gantt · Order',       defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/order' },
  { type: 'gantt-process',    title: 'Gantt · Process',     defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/process' },
  { type: 'gantt-resource',   title: 'Gantt · Resource',    defaultW: 7, defaultH: 4, redirect: '/dashboard/gantt/resource' },
]

const STORAGE_KEY = 'dashboard-layout-v1'

const DEFAULT_LAYOUT: WidgetLayout[] = [
  { id: 'w-kpi',         type: 'kpi',               title: 'KPI Overview',     x: 0, y: 0, w: 8, h: 3, visible: true },
  { id: 'w-orders',      type: 'orders',             title: 'Orders',           x: 0, y: 3, w: 6, h: 4, visible: true },
  { id: 'w-resources',   type: 'resources',          title: 'Resources',        x: 8, y: 0, w: 4, h: 4, visible: true },
  { id: 'w-disruptions', type: 'disruptions-chart',  title: 'Disruptions',      x: 6, y: 3, w: 6, h: 4, visible: true },
  { id: 'w-gantt-order', type: 'gantt-order',        title: 'Gantt · Order',    redirect: '/dashboard/gantt/order',    x: 0, y: 7, w: 12, h: 4, visible: true },
]

function loadLayout(): WidgetLayout[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return JSON.parse(JSON.stringify(DEFAULT_LAYOUT))
}

function saveLayout(layout: WidgetLayout[]) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(layout)) } catch { /* ignore */ }
}

export function useDashboardLayout() {
  const layout = ref<WidgetLayout[]>(loadLayout())
  const editMode = ref(false)
  const addPanelOpen = ref(false)

  const visibleWidgets = computed(() => layout.value.filter(w => w.visible))

  function toggleEdit() {
    editMode.value = !editMode.value
    if (!editMode.value) saveLayout(layout.value)
  }

  function removeWidget(id: string) {
    const w = layout.value.find(w => w.id === id)
    if (w) w.visible = false
    saveLayout(layout.value)
  }

  function addWidget(def: WidgetDef) {
    // Re-show if already exists
    const existing = layout.value.find(w => w.type === def.type && !w.visible)
    if (existing) {
      existing.visible = true
      saveLayout(layout.value)
      return
    }
    // Find a free row
    const maxY = layout.value.reduce((m, w) => Math.max(m, w.y + w.h), 0)
    const id = `w-${def.type}-${Date.now()}`
    layout.value.push({
      id,
      type: def.type,
      title: def.title,
      redirect: def.redirect,
      x: 0,
      y: maxY,
      w: def.defaultW,
      h: def.defaultH,
      visible: true,
    })
    saveLayout(layout.value)
  }

  function updateWidget(id: string, patch: Partial<Pick<WidgetLayout, 'x' | 'y' | 'w' | 'h'>>) {
    const w = layout.value.find(w => w.id === id)
    if (w) Object.assign(w, patch)
  }

  function commitLayout() {
    saveLayout(layout.value)
  }

  function resetLayout() {
    layout.value = JSON.parse(JSON.stringify(DEFAULT_LAYOUT))
    saveLayout(layout.value)
  }

  const addableWidgets = computed(() =>
    WIDGET_DEFS.filter(def => !layout.value.some(w => w.type === def.type && w.visible))
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
