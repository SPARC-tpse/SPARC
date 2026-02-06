<script setup lang="ts">
import { computed } from 'vue'
import { useDisruptionDraft } from '~/composables/useDisruptionDraft'

definePageMeta({ layout: false })

const { hasDraft } = useDisruptionDraft()

if (hasDraft.value) {
  await navigateTo('/disruption/new', { replace: true })
} else {
  await navigateTo('/disruption/overview', { replace: true })
}
</script>

<template>
  <div></div>
</template>