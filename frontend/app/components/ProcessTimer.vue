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
                [`${props.timerType}_seconds`]: seconds.value
            }

            const response = await $fetch(`${API_BASE_URL}/api/process/timing/${props.processId}/`, {
                method: 'PUT',
                body: payload,
                headers: {
                    'Content-Type': 'application/json'
                }
            })

            console.log('Time saved:', response)
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
    <label class="text-sm font-medium label-text">
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
        class="px-3 py-2 rounded-lg text-sm font-semibold border transition-colors"
        :class="[
          seconds === 0 ? 'opacity-50 cursor-not-allowed' : '',
          isDarkMode
            ? 'border-gray-700 bg-gray-800 text-slate-200 hover:bg-gray-700'
            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100'
        ]"
      >
        Reset
      </button>

      <!-- Time Display -->
      <div
        class="px-4 py-2 rounded-lg font-mono text-lg font-bold"
        :class="[
          isRunning ? 'animate-pulse' : '',
          isDarkMode
            ? 'bg-gray-800 text-green-400 border border-gray-700'
            : 'bg-slate-100 text-green-600 border border-slate-300'
        ]"
      >
        {{ formattedTime }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.label-text {
  @apply text-slate-300;
}
.light-mode .label-text {
  @apply text-slate-600;
}
</style>