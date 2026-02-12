<script setup lang="js">
    import { useTheme } from '~/composables/useTheme'
    definePageMeta({
        layout: 'custom'
    })

    const { isDarkMode } = useTheme();
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar
          title="Orders · New"
          :can-submit="canSubmit"
          :show-reset="true"
          :show-create="true"
          create-label="Create"
          @reset="resetForm"
          @submit="submitOrder"
        />

        <main class="max-w-5xl mx-auto p-6 space-y-4">

        </main>
    </div>
</template>

<style scoped>
    .input {
      @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
    }
    .dark-mode .input {
      @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
    }
    .light-mode .input {
      @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
    }

    .dark-mode .disabled-input {
      @apply bg-gray-900 text-slate-500;
    }
    .light-mode .disabled-input {
      @apply bg-slate-100 text-slate-500;
    }

    .dark-mode .label-text {
      @apply text-slate-300;
    }
    .light-mode .label-text {
      @apply text-slate-600;
    }
</style>