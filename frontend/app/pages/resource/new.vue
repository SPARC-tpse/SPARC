<script setup lang="js">
import { ref, computed } from 'vue'
import { useRouter } from '#app'

definePageMeta({ layout: 'custom' })

const { theme } = useAppTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const form = ref({ name: "", type: "Machinery", status: "available" })
const canSubmit = computed(() => form.value.name && form.value.type && form.value.status)

async function submit() {
    const mapping = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }
    try {
        await $fetch(`${API_BASE_URL}/api/resource/post`, {
            method: 'POST',
            body: { ...form.value, status: mapping[form.value.status] }
        })
        router.push('/resource/overview')
    } catch (e) { alert('Error during creation') }
}
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar title="Resources · New" :can-submit="canSubmit" :show-create="true" @submit="submit" @reset="() => router.push('/resource/overview')" />

    <main :class="theme.container">
      <section :class="theme.card">
        <div :class="theme.formGrid">
            <label :class="theme.label">
              Name
              <input v-model="form.name" :class="theme.input" placeholder="Enter resource name..."/>
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
  </div>
</template>