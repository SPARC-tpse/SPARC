<script setup>
    // Redirect /order to /order/overview
    definePageMeta({
    layout: false
    })

    navigateTo('/dashboard', { replace: true })
</script>

<template>
  <div></div>
</template>