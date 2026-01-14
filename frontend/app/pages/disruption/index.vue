<script setup>
    // Redirect /disruption to /disruption/overview
    definePageMeta({
        layout: false
    })

    navigateTo('/disruption/overview', { replace: true })
</script>

<template>
  <div></div>
</template>