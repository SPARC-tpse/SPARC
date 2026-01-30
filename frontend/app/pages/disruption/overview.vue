<script setup lang="js">
import { ref, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'

definePageMeta({
  layout: 'custom'
})

const { isDarkMode } = useTheme()
const { fetchDisruptions } = useApi()
const disruptions = ref([])

onMounted(async () => {
  try {
    // Nutzt die zentrale API-Funktion
    disruptions.value = await fetchDisruptions()
  } catch (err) {
    console.error("Fehler beim Laden der Disruptions:", err)
  }
})

function editDisruption(disruptionId) {
  // Korrekter Pfad inklusive Unterordner
  navigateTo(`/disruption/edit/${disruptionId}`)
}
</script>

<template>
  <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
    <Topbar
      title="Disruptions · Overview"
      :show-reset="false"
      :show-create="false"
    />

    <main class="max-w-5xl mx-auto p-6">
      <section
        class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-slate-900 shadow-black'
          : 'border-slate-200 bg-white shadow-slate-200'"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <h3 class="font-semibold">Disruptions overview</h3>
            <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
              {{ disruptions.length }} total
            </span>
          </div>
          <NuxtLink
            to="/disruption/new"
            class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg"
          >
            + New Disruption
          </NuxtLink>
        </div>

        <div class="grid gap-2">
          <div class="grid grid-cols-[1.2fr,0.8fr,1fr,1fr,1fr,1fr,80px] gap-2 text-xs"
               :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
            <span>Name</span>
            <span>ID</span>
            <span>Start</span>
            <span>End</span>
            <span>Resource</span>
            <span>Type</span>
            <span>Action</span>
          </div>

          <div
            v-for="disruption in disruptions"
            :key="disruption.id"
            class="grid grid-cols-[1.2fr,0.8fr,1fr,1fr,1fr,1fr,80px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
            :class="isDarkMode
              ? 'border-gray-700 bg-gray-700'
              : 'border-slate-200 bg-slate-50 hover:bg-slate-100'"
          >
            <span class="font-medium">{{ disruption.name }}</span>
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ disruption.id }}</span>
            
            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">
              {{ new Date(disruption.start).toLocaleString('en-GB', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              }) }}
            </span>

            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">
              {{ disruption.end ? new Date(disruption.end).toLocaleString('en-GB', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              }) : '—' }}
            </span>

            <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">
              {{ disruption.resource_name || '—' }}
            </span>

            <span>
              <span class="px-2 py-1 rounded-full text-xs font-semibold bg-amber-600 text-amber-50">
                {{ disruption.type_name }}
              </span>
            </span>

            <button
              @click="editDisruption(disruption.id)"
              class="px-2 py-1 text-xs rounded border transition-colors"
              :class="isDarkMode
                ? 'border-gray-600 hover:bg-gray-600 text-slate-200'
                : 'border-slate-300 hover:bg-slate-200 text-slate-700'"
            >
              Edit
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dark-mode {
  @apply min-h-screen bg-slate-950 text-slate-100;
}
.light-mode {
  @apply min-h-screen bg-slate-50 text-slate-900;
}
</style>