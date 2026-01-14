<script setup>
    // Redirect /order to /order/overview
    definePageMeta({
    layout: false
    })

    navigateTo('/order/overview', { replace: true })
</script>

<template>
  <div></div>
</template>