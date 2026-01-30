<script setup lang="js">
const props = defineProps({
  title: String,
  buttonLabel: String,
  modelValue: Object, // Hier kommt unser Resource-Objekt rein
  canSubmit: Boolean,
  isDarkMode: Boolean
})

const emit = defineEmits(['update:modelValue', 'save', 'cancel'])

// Wir spiegeln das modelValue für v-model
const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      :title="title"
      :can-submit="canSubmit"
      :show-reset="true"
      :show-create="true"
      :create-label="buttonLabel"
      @reset="$emit('cancel')"
      @submit="$emit('save')"
    />

    <main class="max-w-5xl mx-auto p-6 space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label class="flex flex-col gap-1 text-sm label-text">
          Resource Name
          <input v-model="form.name" class="input" />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          ID
          <input :value="form.id || 'Auto-generated'" class="input disabled-input" disabled />
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Type
          <select v-model="form.type" class="input">
            <option disabled value="">-- choose type --</option>
            <option value="machinery">Machinery</option>
            <option value="worker">Worker</option>
            <option value="tool">Tool</option>
            <option value="vehicle">Vehicle</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
          Status
          <select v-model="form.status" class="input">
            <option disabled value="">-- choose status --</option>
            <option value="available">Available / Ready</option>
            <option value="in-use">In Use / Active</option>
            <option value="maintenance">Under Maintenance</option>
            <option value="offline">Offline / Unavailable</option>
          </select>
        </label>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Hier das CSS aus deiner Datei reinkopieren */
.input { @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors; }
.dark-mode .input { @apply border-gray-700 bg-gray-800 text-slate-100; }
/* ... usw ... */
</style>