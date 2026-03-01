<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

const props = defineProps({
  modelList: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  single: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])
const { isDarkMode } = useTheme()

const searchQuery = ref('')
const isOpen = ref(false)
const containerRef = ref(null)

const availableOptions = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return props.modelList.filter(element => {
    const isSelected = props.modelValue.some(selected => selected.id === element.id)
    const matchesSearch = element.name.toLowerCase().includes(query)
    return matchesSearch && !isSelected
  })
})

function selectElement(element) {
  emit('update:modelValue', props.single ? [element] : [...props.modelValue, element])
  searchQuery.value = ''
  if (props.single) isOpen.value = false
}

function removeElement(elementId) {
  emit('update:modelValue', props.modelValue.filter(w => w.id !== elementId))
}

function closeDropdown(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', closeDropdown))
onUnmounted(() => document.removeEventListener('click', closeDropdown))
</script>

<template>
  <div ref="containerRef" class="relative w-full">
    <div
      class="min-h-[40px] w-full rounded-lg border px-2 py-1.5 flex flex-wrap gap-2 items-center cursor-text transition-colors"
      :class="[
        isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-slate-300 bg-white',
        isOpen ? (isDarkMode ? 'ring-1 ring-pink-500 border-pink-500' : 'ring-1 ring-indigo-500 border-indigo-500') : ''
      ]"
      @click="isOpen = true"
    >
      <span
        v-for="element in modelValue"
        :key="element.id"
        class="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium border"
        :class="isDarkMode ? 'bg-gray-700 border-gray-600 text-slate-200' : 'bg-indigo-50 border-indigo-100 text-indigo-700'"
      >
        {{ element.name }}
        <button @click.stop="removeElement(element.id)" class="hover:text-red-500 font-bold px-0.5">&times;</button>
      </span>

      <input
        v-model="searchQuery"
        class="flex-1 min-w-[60px] bg-transparent outline-none text-sm"
        :class="isDarkMode ? 'text-slate-100 placeholder-slate-500' : 'text-slate-900 placeholder-slate-400'"
        placeholder="Select..."
        @focus="isOpen = true"
      />
    </div>

    <ul
      v-if="isOpen && availableOptions.length > 0"
      class="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border shadow-lg py-1"
      :class="isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-slate-200'"
    >
      <li
        v-for="element in availableOptions"
        :key="element.id"
        class="px-3 py-2 text-sm cursor-pointer transition-colors"
        :class="isDarkMode ? 'text-slate-200 hover:bg-gray-700' : 'text-slate-700 hover:bg-slate-100'"
        @click="selectElement(element)"
      >
        {{ element.name }}
      </li>
    </ul>
  </div>
</template>