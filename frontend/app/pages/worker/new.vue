<script setup lang="js">
import { ref, computed, inject, watchEffect } from 'vue'
import { useRouter } from '#app'
import { useWorkerDraft} from "~/composables/useWorkerDraft.ts";

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Workers · New',
    showReset: true,
    showCreate: true,
    createLabel: 'Create',
  },
})

const registerTopbarActions = inject('registerTopbarActions')



const { theme } = useAppTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const { draft, resetDraft } = useWorkerDraft()

const workerName = computed({
  get: () => draft.value.name,
  set: (v) => { draft.value.name = v },
})

const canSubmit = computed(() => workerName.value.length > 1)

function resetForm() {
    resetDraft()
}

async function submitWorker() {
    if (!canSubmit.value) return
    try {
        await $fetch(`${API_BASE_URL}/api/worker/post`, {
            method: 'POST',
            body: { name: workerName.value }
        })
        resetDraft()
        await router.push('/worker/overview') // TODO: await notwendig?
    } catch (error) { alert('Failed to create worker') }
}

watchEffect(() => {
    registerTopbarActions({
        reset: resetForm,
        submit: submitWorker,
        canSubmit
    })
})
</script>

<template>
  <div :class="theme.pageWrapper">
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