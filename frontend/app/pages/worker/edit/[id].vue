<script setup lang="js">
import { ref, onMounted, computed, inject, watchEffect } from 'vue'
import { useRoute, useRouter } from '#app'

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Workers · Edit',
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
const workerId = route.params.id

const worker = ref({ name: '' })
const canSubmit = computed(() => worker.value.name.length > 1)

async function loadWorker() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/worker/get/${workerId}/`)
        worker.value = response
    } catch (error) {
        console.error(error)
        router.push('/worker/overview')
    }
}

async function updateWorker() {
    if (!canSubmit.value) return
    try {
        await $fetch(`${API_BASE_URL}/api/worker/put/${workerId}/`, {
            method: 'PUT',
            body: { name: worker.value.name }
        })
        router.push('/worker/overview')
    } catch (error) { alert('Failed to update worker') }
}

function resetForm() {
    router.push('/worker/overview')
}

watchEffect(() => {
    registerTopbarActions?.({ reset: resetForm, submit: updateWorker, canSubmit })
})

onMounted(loadWorker)
</script>

<template>
  <main :class="theme.container">
    <section :class="theme.card" class="max-w-2xl mx-auto">
      <h3 class="font-semibold text-lg mb-4">Edit Worker Details</h3>

      <div class="space-y-4">
        <label :class="theme.label">
          Worker Name
          <input
            v-model="worker.name"
            :class="theme.input"
            placeholder="e.g. John Doe"
            autofocus
            @keyup.enter="updateWorker"
          />
        </label>

        <div class="text-xs opacity-50 italic">
          ID: #{{ workerId }}
        </div>
      </div>
    </section>
  </main>
</template>