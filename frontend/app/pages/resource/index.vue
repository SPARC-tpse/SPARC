<script setup>
    // Redirect root to orders overview by default
    definePageMeta({
        layout: false
    })

    // Immediately redirect on mount
    navigateTo('/resource/overview', { replace: true })
</script>

<template>
  <div></div>
</template>
