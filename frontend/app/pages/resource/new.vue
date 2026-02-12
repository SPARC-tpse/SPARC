<script setup lang="js">
import { ref, computed } from 'vue'
import { useRouter } from '#app'
import { useTheme } from '~/composables/useTheme'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const form = ref({ name: "", type: "", status: "" })
const canSubmit = computed(() => form.value.name && form.value.type && form.value.status)

async function submit() {
    const mapping = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }
    try {
        await $fetch(`${API_BASE_URL}/api/resource/post`, {
            method: 'POST',
            body: { ...form.value, status: mapping[form.value.status] }
        })
        router.push('/resource/overview')
    } catch (e) { alert('Error') }
}
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar title="Resources · New" :can-submit="canSubmit" :show-create="true" @submit="submit" />
    <main class="max-w-5xl mx-auto p-6 grid grid-cols-2 gap-4">
        <label class="flex flex-col text-sm">Name <input v-model="form.name" class="input"/></label>
        <label class="flex flex-col text-sm">Type
          <select v-model="form.type" class="input">
            <option value="Machinery">Machinery</option>
            <option value="Worker">Worker</option>
            <option value="Tool">Tool</option>
            <option value="Vehicle">Vehicle</option>
          </select>
        </label>
        <label class="flex flex-col text-sm">Status
          <select v-model="form.status" class="input">
            <option value="available">Available</option>
            <option value="in-use">In Use</option>
            <option value="maintenance">Maintenance</option>
            <option value="offline">Offline</option>
          </select>
        </label>
    </main>
  </div>
</template>

<style scoped>
.input { @apply border rounded p-2 bg-transparent; }
.dark-mode .input { @apply border-gray-700 bg-gray-800; }
</style>