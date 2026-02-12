<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const stepId = String(route.params.id ?? '')
const orderId = stepId.includes('-') ? stepId.slice(0, stepId.lastIndexOf('-')) : ''
const returnPath = orderId ? `/order/edit/${orderId}` : '/order/overview'

const processStep = ref({
  id: stepId,
  name: '',
  worker: '',
  resource: '',
  status: 'Planned',
  setupTime: '',
  disruptionTime: '',
  waitingTime: '',
  processTime: '',
  quantity: '',
  measurementResult: ''
})

const canSubmit = computed(() => Boolean(processStep.value.name && processStep.value.worker))

function loadProcessStep() {
  // TODO: Fetch from backend
  processStep.value = {
    id: stepId,
    name: 'Assembly',
    worker: 'Lena',
    resource: 'Machine A',
    status: 'Running',
    setupTime: '00:30',
    disruptionTime: '00:10',
    waitingTime: '00:15',
    processTime: '02:10',
    quantity: 120,
    measurementResult: 'OK'
  }
}

const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;
const allResources = ref([]);

async function loadResources() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/resource/list`);
        allResources.value = response || [];
    } catch (e) { console.error(e); }
}

async function updateProcessStep() {
  if (!canSubmit.value) return

  // TODO: Send to backend
  console.log('Updating process step:', processStep.value)

  await navigateTo(returnPath)
}

function cancelEdit() {
  navigateTo(returnPath)
}

onMounted(() => {
  loadProcessStep()
  loadResources();
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Process Steps Edit"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Update"
      @reset="cancelEdit"
      @submit="updateProcessStep"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div
        class="rounded-xl border p-4 flex items-center justify-between shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div>
          <div class="text-xs uppercase tracking-widest" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            Linked order
          </div>
          <div class="text-sm font-semibold" :class="isDarkMode ? 'text-slate-100' : 'text-slate-800'">
            {{ orderId || 'Not linked' }}
          </div>
        </div>
        <NuxtLink
          v-if="orderId"
          :to="returnPath"
          class="px-3 py-2 text-sm rounded-lg border transition-colors"
          :class="isDarkMode
            ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
            : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
        >
          Back to order
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name
          <input v-model="processStep.name" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="processStep.id" class="input disabled-input" disabled />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Worker
          <input v-model="processStep.worker" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource
          <select v-model="processStep.resource" class="input">
            <option value="" disabled hidden>-- Choose Resource --</option>

            <option v-for="res in allResources" :key="res.id" :value="res.name">
              {{ res.name }}
            </option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="processStep.status" class="input">
            <option>Planned</option>
            <option>Running</option>
            <option>Paused</option>
            <option>Done</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Quantity
          <input v-model="processStep.quantity" type="number" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Setup time
          <input v-model="processStep.setupTime" placeholder="hh:mm" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Disruption time
          <input v-model="processStep.disruptionTime" placeholder="hh:mm" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Waiting time
          <input v-model="processStep.waitingTime" placeholder="hh:mm" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text">
          Process time
          <input v-model="processStep.processTime" placeholder="hh:mm" class="input" />
        </label>
        <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
          Measurement result
          <textarea v-model="processStep.measurementResult" rows="3" class="input" />
        </label>
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
