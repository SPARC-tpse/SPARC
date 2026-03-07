import { ref, onMounted, onUnmounted, type Ref } from 'vue'

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
  priority: number
  status: number
  comments: string
  bom_files: OrderFile[]
  general_files: OrderFile[]
}

export interface ResourceType {
  id: number
  name: string
}

export interface Resource {
  id: number
  name: string
  type: ResourceType
  status: number
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

export interface Process {
  name: string,
  approximated_time: number,
  resource: number,
  order: number,
}

export function useDashboardData() {
  const orders: Ref<Order[]> = ref([])
  const resources: Ref<Resource[]> = ref([])
  const processes: Ref<Process[]> = ref([])
  const kpis: Ref<KPI[]> = ref([])
  const disruptions: Ref<Disruption[]> = ref([])
  const wsConnected: Ref<Boolean> = ref(false)
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  async function loadData() {
    const config = useRuntimeConfig()
    const base: string = config.public.apiBaseUrl

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

    // Process
    try {
      const response = await $fetch<Process[]>(`${base}/api/process/get/`)
      processes.value = response.map(p => ({
        id:                p.id,
        name:              p.name,
        approximated_time: p.approximated_time,
        resource:          p.resource?.id ?? null,
        order:             p.order?.id ?? p.order,
      }))
    } catch (err) {
      console.error('Failed to load processes:', err)
    }

    // Disruptions
    try {
      disruptions.value = await $fetch<Disruption[]>(`${base}/api/disruption/chart/get/`)
    } catch (err) {
      console.error('Failed to load disruptions:', err)
    }
  }

  function loadMockData() {
    kpis.value = [
      { id: 'k1', label: 'OEE',            value: 84.2, unit: '%',      trend: 'up',     delta: '+2.1%' },
      { id: 'k2', label: 'Throughput',     value: 247,  unit: 'u/h',    trend: 'stable', delta: '±0' },
      { id: 'k3', label: 'Downtime',       value: 3.2,  unit: 'h',      trend: 'down',   delta: '-0.8h' },
      { id: 'k4', label: 'Yield',          value: 97.4, unit: '%',      trend: 'up',     delta: '+0.3%' },
      { id: 'k5', label: 'Orders Done',    value: 18,   unit: '',       trend: 'up',     delta: '+3' },
      { id: 'k6', label: 'Avg Cycle Time', value: 14.6, unit: 'min',    trend: 'down',   delta: '-1.2' },
    ]
  }

  function handleMessage(event: MessageEvent) {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'orders')          orders.value          = data.payload
      if (data.type === 'resources')       resources.value       = data.payload
      if (data.type === 'kpis')            kpis.value            = data.payload
      if (data.type === 'disruptions')     disruptions.value     = data.payload
      if (data.type === 'processes')       processes.value       = data.payload
      //if (data.type === 'gantt-orders')    ganttOrders.value     = data.payload
      //if (data.type === 'gantt-processes') ganttProcesses.value  = data.payload
      //if (data.type === 'gantt-resources') ganttResources.value  = data.payload
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
    orders, resources, kpis, disruptions, processes,
    wsConnected,
  }
}
