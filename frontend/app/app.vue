<script setup lang="ts">
import { ref } from 'vue'

const message = ref(`Hello Nuxt ${2 + 1}!!`)

function changeMessage() {
  message.value = "hello world"
}
</script>

<template>
  <div class="hello">
    {{ message }}
  </div>

  <button class="btn" @click="changeMessage">
    Change Text
  </button>
</template>

<style scoped>
.hello {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 3rem;
  padding: 2rem;
}

.btn {
  margin-left: 2rem;
  padding: 0.5rem 1rem;
  font-size: 1.2rem;
}
</style>
