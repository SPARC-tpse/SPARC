<script setup lang="js">
import { useTheme } from '~/composables/useTheme'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  canSubmit: {
    type: Boolean,
    default: true
  },
  showReset: {
    type: Boolean,
    default: true
  },
  showCreate: {
    type: Boolean,
    default: true
  },
  createLabel: {
    type: String,
    default: 'Create'
  }
})

const emit = defineEmits(['reset', 'submit'])

const { isDarkMode, toggleDarkMode } = useTheme()
</script>

<template>
  <header
    class="flex items-center justify-between border-b px-6 py-4 transition-colors duration-300"
    :class="isDarkMode
      ? 'border-gray-600 bg-gradient-to-r from-indigo-900 via-slate-900 to-pink-900'
      : 'border-slate-200 bg-white text-slate-800 shadow-sm'"
  >
    <div class="font-semibold tracking-[0.12em] uppercase" :class="isDarkMode ? 'text-white' : 'text-indigo-900'">
      SPARC MES · {{ title }}
    </div>

    <div class="flex gap-2 items-center">
      <button
        @click="toggleDarkMode"
        class="mr-2 rounded-full p-2 hover:bg-opacity-20 hover:bg-gray-500 transition"
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        <span v-if="isDarkMode">🌙</span>
        <span v-else>☀️</span>
      </button>

      <button
        v-if="showReset"
        class="rounded-lg border px-3 py-2 text-sm transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-gray-900 text-slate-100 hover:border-pink-700'
          : 'border-slate-300 bg-white text-slate-700 hover:border-indigo-500 hover:text-indigo-600'"
        @click="$emit('reset')"
      >
        Reset
      </button>

      <button
        v-if="showCreate"
        class="rounded-lg px-3 py-2 text-sm font-semibold text-white disabled:opacity-40 transition-all shadow-md"
        :class="canSubmit ? 'bg-gradient-to-r from-indigo-500 to-pink-500' : 'bg-gray-500'"
        :disabled="!canSubmit"
        @click="$emit('submit')"
      >
        {{ createLabel }}
      </button>
    </div>
  </header>
</template>