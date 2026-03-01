<script setup lang="js">
import { ref, computed, onMounted } from 'vue'

definePageMeta({
  layout: 'custom'
})

const { theme } = useAppTheme() // Das zentrale Theme laden
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

// Mock-Daten laden (TODO: Später durch echten API-Call ersetzen)
function loadProcessStep() {
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
        const response = await $fetch(`${API_BASE_URL}/api/resource/get/`);
        allResources.value = response || [];
    } catch (e) { console.error(e); }
}

async function updateProcessStep() {
  if (!canSubmit.value) return
  console.log('Updating process step:', processStep.value)
  await navigateTo(returnPath)
}

onMounted(() => {
  loadProcessStep()
  loadResources();
})
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar
      title="Process Step · Edit"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Update"
      @reset="() => navigateTo(returnPath)"
      @submit="updateProcessStep"
    />

    <main :class="theme.container" class="space-y-6">

      <section :class="theme.card" class="flex items-center justify-between py-3">
        <div>
          <div :class="theme.label" class="mt-0 opacity-70">Linked order</div>
          <div class="text-lg font-bold tracking-tight">
            {{ orderId || 'Standalone Step' }}
          </div>
        </div>
        <NuxtLink :to="returnPath" :class="theme.btnDeleteMode" class="px-4 py-2">
          Back to order
        </NuxtLink>
      </section>

      <section :class="theme.card">
        <h3 class="font-semibold text-lg mb-4">Step Details</h3>

        <div :class="theme.formGrid">
          <label :class="theme.label">
            Step Name
            <input v-model="processStep.name" :class="theme.input" placeholder="e.g. Final Inspection" />
          </label>

          <label :class="theme.label">
            Process ID
            <input :value="processStep.id" :class="theme.inputDisabled" disabled />
          </label>

          <label :class="theme.label">
            Assigned Worker
            <input v-model="processStep.worker" :class="theme.input" placeholder="Enter name..." />
          </label>

          <label :class="theme.label">
            Resource
            <select v-model="processStep.resource" :class="theme.input">
              <option value="" disabled hidden>-- Choose Resource --</option>
              <option v-for="res in allResources" :key="res.id" :value="res.name">
                {{ res.name }}
              </option>
            </select>
          </label>

          <label :class="theme.label">
            Status
            <select v-model="processStep.status" :class="theme.input">
              <option>Planned</option>
              <option>Running</option>
              <option>Paused</option>
              <option>Done</option>
            </select>
          </label>

          <label :class="theme.label">
            Quantity
            <input v-model="processStep.quantity" type="number" :class="theme.input" />
          </label>

          <label :class="theme.label">
            Setup time
            <input v-model="processStep.setupTime" placeholder="hh:mm" :class="theme.input" />
          </label>

          <label :class="theme.label">
            Disruption time
            <input v-model="processStep.disruptionTime" placeholder="hh:mm" :class="theme.input" />
          </label>

          <label :class="theme.label">
            Waiting time
            <input v-model="processStep.waitingTime" placeholder="hh:mm" :class="theme.input" />
          </label>

          <label :class="theme.label">
            Process time
            <input v-model="processStep.processTime" placeholder="hh:mm" :class="theme.input" />
          </label>

          <label :class="theme.label" class="sm:col-span-2">
            Measurement result
            <textarea v-model="processStep.measurementResult" rows="3" :class="theme.input" placeholder="Enter findings here..." />
          </label>
        </div>
      </section>
    </main>
  </div>
</template>