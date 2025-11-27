
<script setup lang="js">
import '../assets/css/tailwind.css'
import { ref } from 'vue'

const tab = ref('new')

const orders = ref([
  {
    id: 'ORD-1042',
    name: 'Test Order',
    start: '27/11/2025',
    end: '28/11/2025',
    target: 1200,
    product: 'Ventil platinen',
    status: 'Running',
    priority: 'High',
    comments: 'set-up phase done.',
    process: [
      { worker: 'Lena', resource: 'test resource', notes: 'test note' },
      { worker: 'Max', resource: 'test resource', notes: 'test note2' }
    ]
  }
])

const newOrder = ref({
  name: '',
  start: '',
  end: '',
  target: '',
  product: '',
  status: 'Planned',
  priority: 'Medium',
  comments: ''
})

const steps = ref([{ worker: '', resource: '', notes: '' }])
const formId = ref(makeId())

function canSubmit() {
  const o = newOrder.value
  return Boolean(o.name && o.start && o.end && o.target && o.product)
}

function makeId() {
  return `ORD-${Math.floor(Math.random() * 100000)}`
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

function submitOrder() {
  if (!canSubmit()) return
  const processSteps = steps.value.filter(step => step.worker || step.resource || step.notes)
  const order = {
    id: formId.value,
    name: newOrder.value.name,
    start: newOrder.value.start,
    end: newOrder.value.end,
    target: Number(newOrder.value.target),
    product: newOrder.value.product,
    status: newOrder.value.status,
    priority: newOrder.value.priority,
    comments: newOrder.value.comments,
    process: processSteps
  }
  orders.value.unshift(order)
  resetForm()
}

function badgeTone(kind, value) {
  const statusTone = {
    Running: 'bg-emerald-600 text-emerald-100',
    Planned: 'bg-blue-600 text-blue-100',
    Paused: 'bg-amber-600 text-amber-100',
    default: 'bg-slate-600 text-slate-100'
  }
  const priorityTone = {
    High: 'bg-pink-600 text-pink-100',
    Medium: 'bg-indigo-600 text-indigo-100',
    default: 'bg-slate-600 text-slate-100'
  }
  return kind === 'status' ? (statusTone[value] || statusTone.default) : (priorityTone[value] || priorityTone.default)
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
            <span class="text-slate-200">{{ order.id }}</span>
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('status', order.status)">
                {{ order.status }}
              </span>
            </span>
            <span class="text-slate-200">{{ order.start }}</span>
            <span class="text-slate-200">{{ order.end }}</span>
            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="badgeTone('priority', order.priority)">
                {{ order.priority }}
              </span>
            </span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
>>>>>>> frontend
