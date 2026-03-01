<script setup lang="js">
import { computed, inject, watchEffect } from 'vue'
import { useRouter } from '#app'
import { useResourceDraft} from "~/composables/useResourceDraft.ts";

definePageMeta({
  layout: 'custom',
  layoutProps: {
    title: 'Resources · New',
    showReset: true,
    showCreate: true,
    createLabel: 'Create',
  },
})

const registerTopbarActions = inject('registerTopbarActions', null)


const { theme } = useAppTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const {draft: form, resetDraft } = useResourceDraft()

// robuster: keine Truthy-Fallen, keine Whitespaces
const canSubmit = computed(() => {
  const f = form.value
  return Boolean(
    f.name?.trim()?.length > 0 &&
    f.type?.trim()?.length > 0 &&
    f.status?.trim()?.length > 0
  )
})

async function submit() {
    if (!canSubmit.value) return
    const mapping = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }
    try {
        await $fetch(`${API_BASE_URL}/api/resource/post/`, {
            method: 'POST',
            body: { ...form.value, status: mapping[form.value.status] }
        })
        resetDraft()
        await router.push('/resource/overview')
    } catch (e) { alert('Error during creation') }
}

function resetForm() {
    resetDraft()
}

watchEffect(() => {
  if (!registerTopbarActions) return
  registerTopbarActions({
    reset: resetForm,
    submit,
    canSubmit,
  })
})
</script>

<template>
  <div :class="theme.pageWrapper">
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