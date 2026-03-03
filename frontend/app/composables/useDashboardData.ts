import { ref, onMounted, onUnmounted } from 'vue'

export interface OrderFile {
  id: number
  file: string        // URL
  file_type: 'bom' | 'general'
  name?: string
}

export interface Order {
  id: number
  name: string
  order_number: string
  target_amount: number
  order_files: OrderFile[]
  start_date: string        // was "start"
  end_date: string
  product_name: string
  priority: 'low' | 'medium' | 'high'
  status: string
  comments: string
  bom_files: OrderFile[]
  general_files: OrderFile[]
  approximated_time: number | null
}

export interface ResourceType {
  id: number
  name: string
}

export interface Resource {
  id: number
  name: string
  type: ResourceType
  status: string
}

export interface KPI {
  id: string
  label: string
  value: number | string
  unit?: string
  trend?: 'up' | 'down' | 'stable'
  delta?: string
}

export interface Disruption {
  duration: string
  frequency: number
}

export interface GanttItem {
  id: string
  name: string
  start: number   // 0–100 percentage
  duration: number // 0–100 percentage
  color: string
  status: string
}

export function useDashboardData() {
  const orders = ref<Order[]>([])
  const resources = ref<Resource[]>([])
  const kpis = ref<KPI[]>([])
  const disruptions = ref<Disruption[]>([])
  const ganttOrders = ref<GanttItem[]>([])
  const ganttProcesses = ref<GanttItem[]>([])
  const ganttResources = ref<GanttItem[]>([])
  const wsConnected = ref(false)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  async function loadData() {
    const config = useRuntimeConfig()
    const base = config.public.apiBaseUrl

    // Order
    try {
      orders.value = await $fetch<Order[]>(`${base}/api/order/get/`)
    } catch (err) {
      console.error('Failed to load orders:', err)
    }

    // Resource
    try {
      resources.value = await $fetch<Resource[]>(`${base}/api/resource/get/`)
    } catch (err) {
      console.error('Failed to load resources:', err)
    }

    // update Order for Gnatt
    /*
    try {
      response = await $fetch(`${base}/api/order/approximated_time/${}/`)
    } catch (err) {
      console.error('Failed to load order', err)
    }
    */

    // Disruptions

  }

  function loadMockData() {
    orders.value = [
      {
        id: 1,
        name: 'Order Alpha',
        order_number: '2401',
        target_amount: 100,
        start_date: '2025-01-15',
        end_date: '2025-02-01',
        product_name: 'Widget A',
        priority: 'high',
        status: 'in_progress',
        comments: '',
        order_files: [],
        bom_files: [],
        general_files: [],
      },
      { id: 1, name: 'Order Alpha', order_number: '2401', start_date: '2026-03-01T08:00:00+01:00', approximated_time: 7200,  status: 1 },
      { id: 2, name: 'Order Beta',  order_number: '2402', start_date: '2026-03-03T12:00:00+01:00', approximated_time: 3600,  status: 0 },
      { id: 3, name: 'Order Gamma', order_number: '2403', start_date: '2026-03-03T10:00:00+01:00', approximated_time: 86400, status: 3 }
      //{ id: '1', name: 'ORD-2401', status: 'in-progress', start: '2025-01-15' },
      //{ id: '2', name: 'ORD-2402', status: 'pending',     start: '2025-01-16' },
      //{ id: '3', name: 'ORD-2403', status: 'complete',    start: '2025-01-14' },
      //{ id: '4', name: 'ORD-2404', status: 'delayed',     start: '2025-01-13' },
      //{ id: '5', name: 'ORD-2405', status: 'in-progress', start: '2025-01-17' },
      //{ id: '6', name: 'ORD-2406', status: 'pending',     start: '2025-01-18' },
    ]
    resources.value = [
      { id: 1, name: 'CNC-01',   type: { id: 1, name: 'Machine' },  status: 1 },
      { id: 2, name: 'LATHE-01', type: { id: 1, name: 'Machine' },  status: 0 },
      { id: 3, name: 'WELD-01',  type: { id: 2, name: 'Operator' }, status: 2 },
    ]
    kpis.value = [
      { id: 'k1', label: 'OEE',            value: 84.2, unit: '%',      trend: 'up',     delta: '+2.1%' },
      { id: 'k2', label: 'Throughput',     value: 247,  unit: 'u/h',    trend: 'stable', delta: '±0' },
      { id: 'k3', label: 'Downtime',       value: 3.2,  unit: 'h',      trend: 'down',   delta: '-0.8h' },
      { id: 'k4', label: 'Yield',          value: 97.4, unit: '%',      trend: 'up',     delta: '+0.3%' },
      { id: 'k5', label: 'Orders Done',    value: 18,   unit: '',       trend: 'up',     delta: '+3' },
      { id: 'k6', label: 'Avg Cycle Time', value: 14.6, unit: 'min',    trend: 'down',   delta: '-1.2' },
    ]
    disruptions.value = [
      { duration: '0–5m',   frequency: 14 },
      { duration: '5–15m',  frequency: 9 },
      { duration: '15–30m', frequency: 6 },
      { duration: '30–60m', frequency: 3 },
      { duration: '1–2h',   frequency: 2 },
      { duration: '>2h',    frequency: 1 },
    ]
    ganttOrders.value = [
      { id: 'go1', name: 'ORD-2401', start: 8,  duration: 38, color: '#3b82f6', status: 'in-progress' },
      { id: 'go2', name: 'ORD-2402', start: 30, duration: 22, color: '#f59e0b', status: 'pending' },
      { id: 'go3', name: 'ORD-2403', start: 0,  duration: 55, color: '#10b981', status: 'complete' },
      { id: 'go4', name: 'ORD-2404', start: 50, duration: 28, color: '#ef4444', status: 'delayed' },
    ]
    ganttProcesses.value = [
      { id: 'gp1', name: 'Cutting',  start: 0,  duration: 25, color: '#8b5cf6', status: 'complete' },
      { id: 'gp2', name: 'Welding',  start: 20, duration: 35, color: '#f59e0b', status: 'in-progress' },
      { id: 'gp3', name: 'Assembly', start: 50, duration: 30, color: '#3b82f6', status: 'pending' },
      { id: 'gp4', name: 'QC',       start: 75, duration: 20, color: '#10b981', status: 'pending' },
    ]
    ganttResources.value = [
      { id: 'gr1', name: 'CNC-01',   start: 5,  duration: 45, color: '#3b82f6', status: 'busy' },
      { id: 'gr2', name: 'LATHE-01', start: 0,  duration: 18, color: '#f59e0b', status: 'maintenance' },
      { id: 'gr3', name: 'WELD-01',  start: 30, duration: 50, color: '#10b981', status: 'busy' },
      { id: 'gr4', name: 'ROBOT-01', start: 60, duration: 22, color: '#8b5cf6', status: 'available' },
    ]
  }

  function handleMessage(event: MessageEvent) {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'orders')          orders.value          = data.payload
      if (data.type === 'resources')       resources.value       = data.payload
      if (data.type === 'kpis')            kpis.value            = data.payload
      if (data.type === 'disruptions')     disruptions.value     = data.payload
      if (data.type === 'gantt-orders')    ganttOrders.value     = data.payload
      if (data.type === 'gantt-processes') ganttProcesses.value  = data.payload
      if (data.type === 'gantt-resources') ganttResources.value  = data.payload
    } catch { /* ignore */ }
  }

  function connectWS() {
    try {
      ws = new WebSocket('ws://localhost:3001/dashboard')
      ws.onopen    = () => { wsConnected.value = true }
      ws.onmessage = handleMessage
      ws.onclose   = () => {
        wsConnected.value = false
        reconnectTimer = setTimeout(connectWS, 5000)
      }
      ws.onerror = () => { ws?.close() }
    } catch { /* no WS in dev */ }
  }

  onMounted(() => {
    loadMockData()
    loadData()
    connectWS()
  })

  onUnmounted(() => {
    ws?.close()
    if (reconnectTimer) clearTimeout(reconnectTimer)
  })

  return {
    orders, resources, kpis, disruptions,
    ganttOrders, ganttProcesses, ganttResources,
    wsConnected,
  }
}
