<script setup lang="js">
import { ref, computed, onUnmounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  initialSeconds: {
    type: Number,
    default: 0
  },
  processId: {
    type: Number,
    required: true
  },
  timerType: {
    type: String,
    required: true // 'setup_time', 'waiting_time', 'process_time'
  }
})

const emit = defineEmits(['timeSaved'])

const { isDarkMode } = useTheme()
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

const seconds = ref(props.initialSeconds)
const isRunning = ref(false)
const intervalId = ref(null)

// Format seconds to HH:MM:SS
const formattedTime = computed(() => {
    const hrs = Math.floor(seconds.value / 3600)
    const mins = Math.floor((seconds.value % 3600) / 60)
    const secs = seconds.value % 60
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

// Start/Stop timer
function toggleTimer() {
    if (isRunning.value) {
        // Stop timer and save
        stopTimer()
        saveTime()
    } else {
        // Start timer
        startTimer()
    }
}

function startTimer() {
    isRunning.value = true
    intervalId.value = setInterval(() => {
        seconds.value++
    }, 1000)
}

function stopTimer() {
    isRunning.value = false
    if (intervalId.value) {
        clearInterval(intervalId.value)
        intervalId.value = null
    }
}

async function saveTime() {
  try {
    const payload = {
      [`${props.timerType}`]: seconds.value
    }
    if (props.timerType === "process_time") {
      const response = await $fetch(`${API_BASE_URL}/api/process/part/post/${props.processId}/`, {
        method: 'POST',
        body: payload,
        headers: {
            'Content-Type': 'application/json'
        }
      });
      emit('update', response);
      seconds.value = 0;
    } else {
      await $fetch(`${API_BASE_URL}/api/process/timing/${props.processId}/`, {
        method: 'PUT',
        body: payload,
        headers: {
            'Content-Type': 'application/json'
        }
      });
    }
    emit('timeSaved', { type: props.timerType, seconds: seconds.value })
  } catch (error) {
    console.error('Failed to save time:', error)
    alert('Failed to save time. Please try again.')
  }
}

function resetTimer() {
  if (confirm('Reset timer? This will delete the recorded time.')) {
    stopTimer()
    seconds.value = 0
    saveTime()
  }
}

// Cleanup on unmount
onUnmounted(() => {
    stopTimer()
})
</script>

<template>
  <div class="space-y-2">
    <label :class="theme.label">
      {{ label }}
    </label>

    <div class="flex items-center gap-2">
      <!-- Start/Stop Button -->
      <button
        @click="toggleTimer"
        class="px-3 py-2 rounded-lg text-sm font-semibold transition-all shadow-sm"
        :class="isRunning
          ? 'bg-red-600 hover:bg-red-700 text-white'
          : 'bg-green-600 hover:bg-green-700 text-white'"
      >
        {{ isRunning ? '⏸ Stop & Save' : '▶ Start' }}
      </button>

      <!-- Reset Button -->
      <button
        @click="resetTimer"
        :disabled="seconds === 0"
        :class="[
          theme.timerResetBtn,
          seconds === 0 ? 'opacity-50 cursor-not-allowed' : ''
        ]"
      >
        Reset
      </button>

      <!-- Time Display -->
      <div
        :class="[
          theme.timerDisplay,
          isRunning ? 'animate-pulse' : ''
        ]"
      >
        {{ formattedTime }}
      </div>
    </div>
  </div>
</template>
