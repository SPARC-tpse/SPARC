// composables/useTheme.js
import { ref } from 'vue'

const isDarkMode = ref(true)

export const useTheme = () => {
  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
  }

  return {
    isDarkMode,
    toggleDarkMode
  }
}