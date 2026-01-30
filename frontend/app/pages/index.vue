<script setup>
    // Redirect root to orders overview by default
    definePageMeta({
        layout: false
    })

    // Immediately redirect on mount
    // TODO: redirect to dashboard once finished
    navigateTo('/dashboard', { replace: true })
</script>

<template>
  <div></div>
</template>
