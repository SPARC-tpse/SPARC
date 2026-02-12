<script setup>
    // Redirect /worker to /worker/overview
    definePageMeta({
        layout: false
    })

    navigateTo('/worker/overview', { replace: true })
</script>

<template>
  <div></div>
</template>