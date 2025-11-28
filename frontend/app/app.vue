
<script setup lang="ts">
import '../assets/css/tailwind.css'
import { computed, ref, onMounted } from 'vue'

const tab = ref<'new' | 'overview'>('new')

type ApiStatus = 'not_started' | 'in_progress' | 'done' | 'cancelled'
type ApiPriority = 'low' | 'middle' | 'high'

type UiStatus = 'Planned' | 'Running' | 'Paused' | 'Done'
type UiPriority = 'High' | 'Medium' | 'Low'

type OrderStatus = UiStatus
type Priority = UiPriority

interface Order {
  id: string
  order_id: string
  name: string
  target_amount: number
  start_date: string
  end_date: string
  product_name: string
  priority: ApiPriority
  status: ApiStatus
  comments: string
  created_at: string
}

const orders = ref<Order[]>([])

const newOrder = ref({
  name: '',
  start: '',
  end: '',
  target: '',
  product: '',
  status: 'Planned' as OrderStatus,
  priority: 'Medium' as Priority,
  comments: ''
})

function uiStatusToApi(status: UiStatus): ApiStatus {
  if (status === 'Running') return 'in_progress'
  if (status === 'Done') return 'done'
  if (status === 'Paused') return 'cancelled'
  return 'not_started'
}

function apiStatusToUi(status: ApiStatus): UiStatus {
  if (status === 'in_progress') return 'Running'
  if (status === 'done') return 'Done'
  if (status === 'cancelled') return 'Paused'
  return 'Planned'
}

function uiPriorityToApi(priority: UiPriority): ApiPriority {
  if (priority === 'High') return 'high'
  if (priority === 'Low') return 'low'
  return 'middle'
}

function apiPriorityToUi(priority: ApiPriority): UiPriority {
  if (priority === 'high') return 'High'
  if (priority === 'low') return 'Low'
  return 'Medium'
}

async function loadOrders() {
  const res = await fetch('http://localhost:8000/api/orders/')
  if (!res.ok) {
    console.error('Failed to load orders')
    return
  }
  const data = await res.json() as Order[]
  orders.value = data
}

onMounted(() => {
  loadOrders()
})

const steps = ref([{ worker: '', resource: '', notes: '' }])
const formId = ref(makeId())

const canSubmit = computed(() => {
  const o = newOrder.value
  return Boolean(o.name && o.start && o.end && o.target && o.product)
})

function makeId() {
  return `ORD-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2, 5).toUpperCase()}`
}

function addStep() {
  steps.value.push({ worker: '', resource: '', notes: '' })
}

function resetForm() {
  newOrder.value = {
    name: '',
    start: '',
    end: '',
    target: '',
    product: '',
    status: 'Planned',
    priority: 'Medium',
    comments: ''
  }
  steps.value = [{ worker: '', resource: '', notes: '' }]
  formId.value = makeId()
}

async function submitOrder() {
  if (!canSubmit.value) return

  const o = newOrder.value


  function toIsoDate(d: string) {
    const [day, month, year] = d.split('/')
    return `${year}-${month}-${day}`
  }

  const payload = {
    name: o.name,
    order_id: formId.value,
    target_amount: Number(o.target),
    start_date: toIsoDate(o.start),
    end_date: toIsoDate(o.end),
    product_name: o.product,
    priority: uiPriorityToApi(o.priority),
    status: uiStatusToApi(o.status),
    comments: o.comments
  }

  try {
    const res = await fetch('http://localhost:8000/api/orders/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!res.ok) {
      console.error('Failed to create order', await res.text())
      return
    }

    const created = await res.json() as Order

    // Insert new order at the top of list
    orders.value.unshift(created)

    resetForm()
  } catch (err) {
    console.error('Error while creating order', err)
  }
}

function badgeTone(kind: 'status' | 'priority', value: string) {
  const statusTone: Record<string, string> = {
    Running: 'bg-emerald-600 text-emerald-100',
    Planned: 'bg-blue-600 text-blue-100',
    Paused: 'bg-amber-600 text-amber-100',
    default: 'bg-slate-600 text-slate-100'
  }
  const priorityTone: Record<string, string> = {
    High: 'bg-pink-600 text-pink-100',
    Medium: 'bg-indigo-600 text-indigo-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return kind === 'status'
    ? (statusTone[value] || statusTone.default)
    : (priorityTone[value] || priorityTone.default)
}
</script>


<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <header class="flex items-center justify-between border-b border-gray-600 px-6 py-4 bg-gradient-to-r from-indigo-900 via-slate-900 to-pink-900">
      <div class="font-semibold tracking-[0.12em] uppercase text-white">SPARC MES · Orders</div>
      <div class="flex gap-2">
        <button class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-slate-100 hover:border-pink-700" @click="resetForm">
          Reset
        </button>
        <button
          class="rounded-lg px-3 py-2 text-sm font-semibold text-white disabled:opacity-40"
          :class="canSubmit ? 'bg-gradient-to-r from-indigo-500 to-pink-500' : 'bg-gray-800'"
          :disabled="!canSubmit"
          @click="submitOrder"
        >
          Create
        </button>
      </div>
    </header>

    <main class="max-w-5xl mx-auto p-6 space-y-6">
      <div class="inline-flex rounded-xl bg-gray-800 p-1 border border-gray-800 shadow-lg shadow-black">
        <button
          class="px-4 py-2 text-sm font-semibold rounded-lg"
          :class="tab === 'new' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : 'text-slate-200 hover:text-white'"
          @click="tab = 'new'"
        >
          New
        </button>
        <button
          class="px-4 py-2 text-sm font-semibold rounded-lg"
          :class="tab === 'overview' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : 'text-slate-200 hover:text-white'"
          @click="tab = 'overview'"
        >
          Overview
        </button>
      </div>

      <section v-if="tab === 'new'" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Name
            <input v-model="newOrder.name" class="input" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            ID (auto)
            <input :value="formId" class="input bg-gray-800 text-slate-400" disabled />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Target amount
            <input v-model="newOrder.target" type="number" class="input" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Product name
            <input v-model="newOrder.product" class="input" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Start date
            <input
              v-model="newOrder.start"
              type="date"
              inputmode="numeric"
              class="input"
            />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            End date
            <input
              v-model="newOrder.end"
              type="date"
              inputmode="numeric"
              class="input"
            />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Status
            <select v-model="newOrder.status" class="input bg-slate-900 text-white">
              <option>Planned</option>
              <option>Running</option>
              <option>Paused</option>
              <option>Done</option>
            </select>
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300">
            Priority
            <select v-model="newOrder.priority" class="input bg-slate-900 text-white">
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-300 sm:col-span-2">
            Comments
            <textarea v-model="newOrder.comments" rows="3" class="input" />
          </label>
        </div>

        <div class="rounded-xl border border-gray-900 bg-slate-900 p-4 space-y-3 shadow-lg shadow-black">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">Process steps</h3>
            <button class="text-sm text-pink-200 hover:text-pink-100" @click="addStep">+ Add step</button>
          </div>
          <div class="space-y-2">
            <div class="grid grid-cols-[30px,1fr,1fr,1fr] gap-2 text-xs text-slate-400">
              <span>#</span><span>Worker</span><span>Resource</span><span>Notes</span>
            </div>
            <div
              v-for="(step, i) in steps"
              :key="i"
              class="grid grid-cols-[30px,1fr,1fr,1fr] gap-2 items-center rounded-lg border border-gray-700 bg-gray-700 p-2"
            >
              <span class="text-xs text-slate-400">{{ i + 1 }}</span>
              <input v-model="step.worker" class="input h-10" />
              <input v-model="step.resource" class="input h-10" />
              <input v-model="step.notes" class="input h-10" />
            </div>
          </div>
        </div>
      </section>

      <section v-else class="rounded-xl border border-gray-700 bg-slate-900 p-4 space-y-3 shadow-lg shadow-black">
        <div class="flex items-center justify-between">
          <h3 class="font-semibold">Orders overview</h3>
          <span class="text-xs text-slate-300">{{ orders.length }} total</span>
        </div>
        <div class="grid gap-2">
          <div class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr] gap-2 text-xs text-slate-400">
            <span>Name</span><span>ID</span><span>Status</span><span>Start</span><span>End</span><span>Priority</span>
          </div>
          <div
            v-for="order in orders"
            :key="order.id"
            class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr] gap-2 items-center rounded-lg border border-gray-700 bg-gray-700 p-3 text-sm"
          >
       <span class="font-medium">{{ order.name }}</span>
  <span class="text-slate-200">{{ order.order_id }}</span>
  <span>
    <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('status', apiStatusToUi(order.status))">
      {{ apiStatusToUi(order.status) }}
    </span>
  </span>
  <span class="text-slate-200">{{ order.start_date }}</span>
  <span class="text-slate-200">{{ order.end_date }}</span>
  <span>
    <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('priority', apiPriorityToUi(order.priority))">
      {{ apiPriorityToUi(order.priority) }}
    </span>
  </span>
</div>
        </div>
      </section>
    </main>
  </div>
</template>

