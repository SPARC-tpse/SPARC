<script setup lang="js">
import { useTheme } from '~/composables/useTheme'

const { isDarkMode } = useTheme()
const route = useRoute()

const isActive = (path) => {
  return route.path.startsWith(path)
}
</script>

<template>
  <aside class="w-56 border-l p-4 flex flex-col gap-4 transition-colors duration-300"
    :class="isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-white'">

    <h2 class="text-sm font-semibold tracking-wide mb-2" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
      Navigation
    </h2>

    <NuxtLink
      to="/overview"
      class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all"
      :class="[
        isActive('/overview')
          ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
          : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
      ]"
    >
      Overview
    </NuxtLink>

    <!-- Orders button - links to /order/overview -->
    <NuxtLink to="/order/overview"
      class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all" :class="[
        isActive('/order')
          ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
          : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
      ]">
      Orders
    </NuxtLink>

    <!-- Disruptions button - links to /disruption/overview -->
    <NuxtLink to="/disruption/overview"
      class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all" :class="[
        isActive('/disruption')
          ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
          : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
      ]">
      Disruptions
    </NuxtLink>
    <NuxtLink to="/resource/overview"
      class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all" :class="[
        isActive('/resource')
          ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
          : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
      ]">
      Resources
    </NuxtLink>

    <!-- Spacer to push mode indicator to bottom -->
    <div class="mt-auto pt-4 border-t" :class="isDarkMode ? 'border-gray-700' : 'border-slate-200'">
      <div class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
        <span>{{ isDarkMode ? 'Mode: Dark' : 'Mode: Light' }}</span>
      </div>
    </div>

  </aside>
</template>
