<script setup lang="js">
import { ref, computed, inject, watchEffect } from 'vue'
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

const registerTopbarActions = inject('registerTopbarActions')


const { theme } = useAppTheme()
const router = useRouter()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const {draft: form, resetDraft } = useResourceDraft()

const canSubmit = computed(() => form.value.name.length > 0 && form.value.type.length > 0 && form.value.status.length > 0)

async function submit() {
    const mapping = { 'available': 3, 'in-use': 2, 'maintenance': 4, 'offline': 1 }
    try {
        await $fetch(`${API_BASE_URL}/api/resource/post`, {
            method: 'POST',
            body: { ...form.value, status: mapping[form.value.status] }
        })
        resetDraft()
        await router.push('/resource/overview') // TODO: await notwendig?
    } catch (e) { alert('Error during creation') }
}

function resetForm() {
    resetDraft()
}

watchEffect(() => {
    registerTopbarActions({
        reset: resetForm,
        submit,
        canSubmit
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