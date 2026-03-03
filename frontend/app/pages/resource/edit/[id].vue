<script setup lang="js">
import { ref, onMounted, computed, inject, watchEffect } from 'vue'
import { useRoute, useRouter } from '#app'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Resources · Edit',
    showReset: true,
    showCreate: true,
    createLabel: 'Update',
  },
})

const registerTopbarActions = inject('registerTopbarActions')

const { theme } = useAppTheme()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const resId = route.params.id

const form = ref({ name: '', type: '', status: '' })

const statusToStr = { 3: 'available', 2: 'in-use', 4: 'maintenance', 1: 'offline' }
const strToStatus = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }

const canSubmit = computed(() => Boolean(form.value.name?.trim()))

async function load() {
    try {
        const data = await $fetch(`${API_BASE_URL}/api/resource/get/${resId}/`)
        form.value = {
            name: data.name,
            type: data.type,
            status: statusToStr[data.status] || 'available'
        }
    } catch (e) { console.error(e) }
}

async function update() {
    try {
        await $fetch(`${API_BASE_URL}/api/resource/put/${resId}/`, {
            method: 'PUT',
            body: { ...form.value, status: strToStatus[form.value.status] }
        })
        router.push('/resource/overview')
    } catch (e) { alert('Update failed') }
}

function resetForm() {
    router.push('/resource/overview')
}

watchEffect(() => {
  registerTopbarActions?.({ reset: resetForm, submit: update, canSubmit })
})

onMounted(load)
</script>

<template>
  <main :class="theme.container">
    <section :class="theme.card">
      <div :class="theme.formGrid">
          <label :class="theme.label">
            Name
            <input v-model="form.name" :class="theme.input" placeholder="e.g. CNC Machine 01"/>
          </label>

          <label :class="theme.label">
            Type
            <select v-model="form.type" :class="theme.input">
              <option value="Machinery">Machinery</option>
              <option value="Worker">Worker</option>
              <option value="Tool">Tool</option>
              <option value="Vehicle">Vehicle</option>
            </select>
          </label>

          <label :class="theme.label">
            Status
            <select v-model="form.status" :class="theme.input">
              <option value="available">Available</option>
              <option value="in-use">In Use</option>
              <option value="maintenance">Maintenance</option>
              <option value="offline">Offline</option>
            </select>
          </label>
      </div>
    </section>
  </main>
</template>

