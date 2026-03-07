<script setup lang="js">
import { ref, computed, onMounted, inject, watchEffect } from 'vue'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Disruptions · Edit',
    showReset: true,
    showCreate: true,
    createLabel: 'Update',
  },
})

const registerTopbarActions = inject('registerTopbarActions')

const { theme } = useAppTheme()
const route = useRoute()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const disruptionId = route.params.id

const resources = ref([])
const types = ref([])

const disruption = ref({
  id: disruptionId,
  name: '',
  start_date: '',
  end_date: '',
  resource: '',
  type: ''
})

const canSubmit = computed(() => disruption.value.name && disruption.value.resource)

function setNow(field) {
  disruption.value[field] = new Date().toISOString().slice(0, 16)
}

async function loadData() {
  try {
    const [resData, typeData, dispData] = await Promise.all([
      $fetch(`${API_BASE_URL}/api/resource/get/`),
      $fetch(`${API_BASE_URL}/api/disruption-type/get/`),
      $fetch(`${API_BASE_URL}/api/disruption/get/${disruptionId}/`)
    ])

    resources.value = resData
    types.value = typeData

    const toInputFormat = (dateStr) => dateStr ? dateStr.slice(0, 16) : ''

    disruption.value = {
      ...dispData,
      start_date: toInputFormat(dispData.start_date),
      end_date: toInputFormat(dispData.end_date),
      resource: dispData.resource,
      type: dispData.type
    }
  } catch (e) { console.error('Fehler beim Laden:', e) }
}

async function updateDisruption() {
  if (!canSubmit.value) return
  try {
    await $fetch(`${API_BASE_URL}/api/disruption/put/${disruptionId}/`, {
      method: 'PUT',
      body: disruption.value
    })
    await navigateTo('/disruption/overview')
  } catch (e) { console.error('Update failed:', e) }
}

function resetForm() {
  navigateTo('/disruption/overview')
}

watchEffect(() => {
  registerTopbarActions?.({ reset: resetForm, submit: updateDisruption, canSubmit })
})

onMounted(loadData)
</script>

<template>
  <main :class="theme.container">
    <section :class="theme.card">
      <h3 class="font-semibold text-lg mb-2">Edit Disruption Details</h3>

      <div :class="theme.formGrid">
        <label :class="theme.label">
          Name
          <input v-model="disruption.name" :class="theme.input" placeholder="e.g. Belt Jam" />
        </label>

        <label :class="theme.label">
          Internal ID
          <input :value="disruption.id" :class="[theme.input, 'opacity-50 cursor-not-allowed']" disabled />
        </label>

        <div class="flex flex-col">
          <label :class="theme.label">Start</label>
          <div class="flex gap-2 items-end">
            <input v-model="disruption.start_date" type="datetime-local" :class="theme.input" />
            <button type="button" @click="setNow('start_date')" :class="theme.btnDeleteMode" class="h-[42px] px-4">Now</button>
          </div>
        </div>

        <div class="flex flex-col">
          <label :class="theme.label">End</label>
          <div class="flex gap-2 items-end">
            <input v-model="disruption.end_date" type="datetime-local" :class="theme.input" />
            <button type="button" @click="setNow('end_date')" :class="theme.btnDeleteMode" class="h-[42px] px-4">Now</button>
          </div>
        </div>

        <label :class="theme.label">
          Affected Resource
          <select v-model="disruption.resource" :class="theme.input">
            <option disabled value="">-- choose --</option>
            <option v-for="r in resources" :key="r.id" :value="r.id">{{ r.name }}</option>
          </select>
        </label>

        <label :class="theme.label">
          Disruption Type
          <select v-model="disruption.type" :class="theme.input">
            <option disabled value="">-- choose --</option>
            <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </label>
      </div>
    </section>
  </main>
</template>

