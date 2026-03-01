<script setup lang="js">
import { ref, computed } from 'vue'
import { useRouter } from '#app'

definePageMeta({ layout: 'custom' })

const { theme } = useAppTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const workerName = ref('')
const canSubmit = computed(() => workerName.value.length > 1)

function resetForm() {
    workerName.value = ''
}

async function submitWorker() {
    if (!canSubmit.value) return
    try {
        await $fetch(`${API_BASE_URL}/api/worker/post/`, {
            method: 'POST',
            body: { name: workerName.value }
        })
        router.push('/worker/overview')
    } catch (error) { alert('Failed to create worker') }
}
</script>

<template>
  <div :class="theme.pageWrapper">
    <Topbar
      title="Workers · New"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      create-label="Create"
      @reset="resetForm"
      @submit="submitWorker"
    />

    <main :class="theme.container">
      <section :class="theme.card" class="max-w-2xl mx-auto">
        <h3 class="font-semibold text-lg mb-4">Add New Worker</h3>

        <div class="space-y-4">
          <label :class="theme.label">
            Worker Name
            <input
              v-model="workerName"
              :class="theme.input"
              placeholder="e.g. Maxi Musterknabe"
              autofocus
              @keyup.enter="submitWorker"
            />
          </label>

          <div class="p-3 rounded-lg bg-slate-500/5 border border-slate-500/10 text-xs opacity-70 leading-relaxed">
            <strong>Note:</strong> This name will appear in the selection list when creating or editing orders.
          </div>
        </div>
      </section>
    </main>
  </div>
</template>