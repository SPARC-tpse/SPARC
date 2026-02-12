<script setup lang="js">
import { ref, onMounted, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute, useRouter } from '#app'

definePageMeta({
    layout: 'custom'
})

const { isDarkMode } = useTheme()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl
const workerId = route.params.id

const worker = ref({ name: '' })

const canSubmit = computed(() => worker.value.name.length > 1)

async function loadWorker() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/worker/get/${workerId}`, { method: 'GET' })
        worker.value = response
    } catch (error) {
        console.error(error)
        alert('Failed to load worker')
        router.push('/worker/overview')
    }
}

async function updateWorker() {
    if (!canSubmit.value) return
    try {
        await $fetch(`${API_BASE_URL}/api/worker/put/${workerId}`, {
            method: 'PUT',
            body: { name: worker.value.name }
        })
        router.push('/worker/overview')
    } catch (error) {
        console.error(error)
        alert('Failed to update worker')
    }
}

function cancel() {
    router.push('/worker/overview')
}

onMounted(() => {
    loadWorker()
})
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar
          title="Workers · Edit"
          :can-submit="canSubmit"
          :show-reset="true"
          :show-create="true"
          create-label="Update"
          @reset="cancel"
          @submit="updateWorker"
        />

        <main class="max-w-xl mx-auto p-6 space-y-4">
            <div class="rounded-xl border p-6 space-y-4 shadow-lg transition-colors"
                 :class="isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-white'">

                <h3 class="font-semibold text-lg">Edit Worker</h3>

                <label class="flex flex-col gap-1 text-sm label-text">
                    Worker Name
                    <input
                        v-model="worker.name"
                        class="input"
                        autofocus
                        @keyup.enter="updateWorker"
                    />
                </label>
            </div>
        </main>
    </div>
</template>

<style scoped>
    .input { @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors; }
    .dark-mode .input { @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500; }
    .light-mode .input { @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500; }
    .dark-mode .label-text { @apply text-slate-300; }
    .light-mode .label-text { @apply text-slate-600; }
</style>