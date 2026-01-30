<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const orderId = route.params.id

const order = ref({
  id: orderId,
  name: '',
  start_date: '',
  end_date: '',
  target_amount: '',
  product_name: '',
  status: 'Planned',
  priority: 'Medium',
  comments: ''
})

const steps = ref([{ worker: '', resource: '', notes: '' }])

const canSubmit = computed(() => {
  const o = order.value
  return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
})

function addStep() {
  steps.value.push({ worker: '', resource: '', notes: '' })
}

async function loadOrder() {
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;
    const ENDPOINT = '/api/orders/get/'

    try {
        const response = await $fetch(`${API_BASE_URL}${ENDPOINT}${orderId}`, {
            method: 'GET'
        })
        console.log("response data:" + response)
        console.log(response)
        order.value = response
        steps.value = response.process || [{ worker: '', resource: '', notes: '' }]
    } catch (error) {
        console.error('API Error:', error)
        alert('Failed to load order')
    }
}

async function updateOrder() {
    if (!canSubmit.value) return

    const processSteps = steps.value.filter(step => step.worker || step.resource || step.notes)
    const updatedOrder = {
        ...order.value,
        target_amount: Number(order.value.target_amount),
        process: processSteps
    }

    console.log('Updating order:', updatedOrder)

    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;
    const ENDPOINT = '/api/orders/put/'

    try {
      const response = await $fetch(`${API_BASE_URL}${ENDPOINT}${orderId}`, {
        method: 'PUT',
        body: updatedOrder
      })
      // Navigate back to overview
      await navigateTo('/order/overview')
      //return response
    } catch (error) {
      console.error('API Error:', error)
      alert(error)
    }
}

onMounted(() => {
  loadOrder()
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Orders · Edit"
      :can-submit="canSubmit"
      :show-reset="false"
      :show-create="true"
      create-label="Update"
      @submit="updateOrder"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name
          <input v-model="order.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="order.id" class="input disabled-input" disabled />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Target amount
          <input v-model="order.target_amount" type="number" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Product name
          <input v-model="order.product_name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Start date
          <input v-model="order.start_date" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          End date
          <input v-model="order.end_date" type="date" inputmode="numeric" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="order.status" class="input">
            <option>Planned</option>
            <option>Running</option>
            <option>Paused</option>
            <option>Done</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Priority
          <select v-model="order.priority" class="input">
            <option value="1">High</option>
            <option value="2">Medium</option>
            <option value="3">Low</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
          Comments
          <textarea v-model="order.comments" rows="3" class="input" />
        </label>
      </div>

      <div
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-900 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex items-center justify-between">
          <h3 class="font-semibold">Process steps</h3>
          <button
            class="text-sm hover:underline"
            :class="isDarkMode ? 'text-pink-200 hover:text-pink-100' : 'text-pink-600 hover:text-pink-800'"
            @click="addStep"
          >+ Add step</button>
        </div>
        <div class="space-y-2">
          <div class="grid grid-cols-[30px,1fr,1fr,1fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>#</span><span>Worker</span><span>Resource</span><span>Notes</span>
          </div>
          <div
            v-for="(step, i) in steps"
            :key="i"
            class="grid grid-cols-[30px,1fr,1fr,1fr] gap-2 items-center rounded-lg border p-2 transition-colors"
            :class="isDarkMode
              ? 'border-gray-700 bg-gray-700'
              : 'border-slate-200 bg-slate-50'"
          >
            <span class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ i + 1 }}</span>
            <input v-model="step.worker" class="input h-10" />
            <input v-model="step.resource" class="input h-10" />
            <input v-model="step.notes" class="input h-10" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.input {
  @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
}

.dark-mode .input {
  @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
}

.light-mode .input {
  @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
}

.dark-mode .disabled-input {
  @apply bg-gray-900 text-slate-500;
}
.light-mode .disabled-input {
  @apply bg-slate-100 text-slate-500;
}

.dark-mode .label-text {
  @apply text-slate-300;
}
.light-mode .label-text {
  @apply text-slate-600;
}
</style>