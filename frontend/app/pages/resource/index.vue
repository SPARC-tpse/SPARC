<script setup>
    // Redirect root to orders overview by default
    definePageMeta({
        layout: false
    })

    // Immediately redirect on mount
    // TODO: redirect to dashboard once finished
    navigateTo('/resource/overview', { replace: true })
</script>

<template>
  <div></div>
</template>
