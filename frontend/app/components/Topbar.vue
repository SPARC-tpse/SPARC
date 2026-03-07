<script setup lang="js">
const props = defineProps({
  title: { type: String, required: true },
  canSubmit: { type: Boolean, default: true },
  showReset: { type: Boolean, default: true },
  showCreate: { type: Boolean, default: true },
  createLabel: { type: String, default: 'Create' }
})

const emit = defineEmits(['reset', 'submit'])

const { theme, isDarkMode, toggleDarkMode } = useAppTheme()
</script>

<template>
  <header :class="theme.topbar">
    <div :class="theme.topbarTitle">
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
        :class="theme.topbarResetBtn"
        @click="$emit('reset')"
      >
        Reset
      </button>

      <button
        v-if="showCreate"
        :class="[
          theme.topbarSubmitBtn,
          canSubmit ? theme.topbarSubmitActive : theme.topbarSubmitDisabled
        ]"
        :disabled="!canSubmit"
        @click="$emit('submit')"
      >
        {{ createLabel }}
      </button>
    </div>
  </header>
</template>