<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelList: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] },
  single: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])
const { theme } = useAppTheme()

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
      :class="[
        theme.multiSelectContainer,
        isOpen ? theme.multiSelectFocus : ''
      ]"
      @click="isOpen = true"
    >
      <span
        v-for="element in modelValue"
        :key="element.id"
        :class="theme.multiSelectTag"
      >
        {{ element.name }}
        <button @click.stop="removeElement(element.id)" class="hover:text-red-500 font-bold px-0.5">&times;</button>
      </span>

      <input
        v-model="searchQuery"
        :class="theme.multiSelectInput"
        placeholder="Select..."
        @focus="isOpen = true"
      />
    </div>

    <ul
      v-if="isOpen && availableOptions.length > 0"
      :class="theme.multiSelectDropdown"
    >
      <li
        v-for="element in availableOptions"
        :key="element.id"
        :class="theme.multiSelectOption"
        @click="selectElement(element)"
      >
        {{ element.name }}
      </li>
    </ul>
  </div>
</template>