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
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const route = useRoute()
const resId = route.params.id
const router = useRouter()

const form = ref({ name: '', type: '', status: '' })

const canSubmit = computed(() => Boolean(form.value.name?.trim()))

/**
 * Updates the backend with changes made
 * @returns {Promise<void>}
 */
async function update() {
    try {
        await $fetch(`${API_BASE_URL}/api/resource/put/${resId}/`, {
            method: 'PUT',
            body: { ...form.value, status: form.value.status }
        })
        router.push('/resource/overview')
    } catch (e) { alert('Update failed') }
}

/**
 * Cancels the change and redirects to overview
 */
function resetForm() {
    router.push('/resource/overview')
}

/**
 * Loads the Resource by id
 * @returns {Promise<void>}
 */
async function load() {
    try {
        const data = await $fetch(`${API_BASE_URL}/api/resource/get/${resId}/`)
        form.value = {
            name: data.name,
            type: data.type,
            status: data.status
        }
    } catch (e) { console.error(e) }
}

onMounted(load)

watchEffect(() => {
  registerTopbarActions?.({ reset: resetForm, submit: update, canSubmit })
})
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
            <select v-model="form.type.name" :class="theme.input">
              <option value="Machinery">Machinery</option>
              <option value="Worker">Worker</option>
              <option value="Tool">Tool</option>
              <option value="Vehicle">Vehicle</option>
            </select>
          </label>

          <label :class="theme.label">
            Status
            <select v-model="form.status" :class="theme.input">
              <option value=0>Available</option>
              <option value=1>In Use</option>
              <option value=2>Maintenance</option>
              <option value=3>Offline</option>
            </select>
          </label>
      </div>
    </section>
  </main>
</template>

