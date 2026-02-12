<script setup lang="js">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from '#app'
import { useTheme } from '~/composables/useTheme'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const resId = route.params.id

const form = ref({ name: '', type: '', status: '' })

// Mappings
const statusToStr = { 3: 'available', 2: 'in-use', 4: 'maintenance', 1: 'offline' }
const strToStatus = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }

async function load() {
    try {
        const data = await $fetch(`${API_BASE_URL}/api/resource/get/${resId}`)

        form.value = {
            name: data.name,
            type: data.type,
            status: statusToStr[data.status] || 'available'
        }
    } catch (e) { console.error(e) }
}

async function update() {
    try {
        await $fetch(`${API_BASE_URL}/api/resource/put/${resId}`, {
            method: 'PUT',
            body: { ...form.value, status: strToStatus[form.value.status] }
        })
        router.push('/resource/overview')
    } catch (e) { alert('Update failed') }
}

onMounted(load)
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar title="Resources · Edit" :can-submit="true" :show-create="true" create-label="Update" @submit="update" @reset="() => router.push('/resource/overview')"/>
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