<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

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

const steps = ref([{ worker: '', resource: '', name: '' }])
const bomFiles = ref([])
const generalFiles = ref([])

const canSubmit = computed(() => {
  const o = newOrder.value
  return Boolean(o.name && o.start && o.end && o.target && o.product)
})

function addStep() {
  steps.value.push({ worker: '', resource: '', name: '' })
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
  steps.value = [{ worker: '', resource: '', name: '' }]
  bomFiles.value = []
  generalFiles.value = []
}

function handleBomFilesUploaded(files) {
  bomFiles.value = files
  console.log('BOM files updated:', files)
}

function handleGeneralFilesUploaded(files) {
  generalFiles.value = files
  console.log('General files updated:', files)
}

async function submitOrder() {
    if (!canSubmit.value) return

    const processSteps = steps.value.filter(step => step.worker || step.resource || step.name)
    const order = {
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

    console.log('Submitting order:', order)

    try {
        const response = await $fetch(`${API_BASE_URL}/api/order/post`, {
            method: 'POST',
            body: order
        })
        resetForm()
        // alternatively:
        // await navigateTo('/order/overview')
    } catch (error) {
      console.error('API Error:', error);
      const backendMessage =
        error?.data?.error ||
        error?.response?._data?.error ||
        error?.cause?.data?.error

      if (backendMessage) {
        alert(backendMessage)
      } else {
        alert('Unexpected error occurred')
      }
      //throw error
    }
}
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Orders · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitOrder"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Name
          <input v-model="newOrder.name" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Target amount
          <input v-model="newOrder.target" type="number" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Product name
          <input v-model="newOrder.product" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Start date
          <input v-model="newOrder.start" type="date" inputmode="numeric" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          End date
          <input v-model="newOrder.end" type="date" inputmode="numeric" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="newOrder.status" class="input">
            <option>Planned</option>
            <option>Running</option>
            <option>Paused</option>
            <option>Done</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Priority
          <select v-model="newOrder.priority" class="input">
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </label>

        <!-- comments -->
        <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
          Comments
          <textarea v-model="newOrder.comments" rows="3" class="input" />
        </label>
      </div>

      <!-- file uploads
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- bom upload
        <div
          class="rounded-xl border p-4 shadow-lg transition-colors"
          :class="isDarkMode
            ? 'border-gray-900 bg-slate-900 shadow-black'
            : 'border-slate-200 bg-white shadow-slate-200'"
        >
          <FileUpload
            file-type="bom"
            label="Bill of Materials"
            @files-uploaded="handleBomFilesUploaded"
            @file-deleted="handleBomFilesUploaded"
          />
        </div>

        <!-- general files upload
        <div
          class="rounded-xl border p-4 shadow-lg transition-colors"
          :class="isDarkMode
            ? 'border-gray-900 bg-slate-900 shadow-black'
            : 'border-slate-200 bg-white shadow-slate-200'"
        >
          <FileUpload
            file-type="general"
            label="Additional Files"
            @files-uploaded="handleGeneralFilesUploaded"
            @file-deleted="handleGeneralFilesUploaded"
          />
        </div>
      </div>
      -->

      <!-- process steps -->
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
            <span>#</span><span>Worker</span><span>Resource</span><span>Process-step Name</span>
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
            <input v-model="step.name" class="input h-10" />
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