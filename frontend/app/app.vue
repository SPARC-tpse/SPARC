<script setup lang="js">
import { ref } from 'vue'

import OrderView from './components/order.vue'
import DisruptionView from './components/disruption.vue'

const currentView = ref('orders')
const isDarkMode = ref(true)

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
}

const views = {
  orders: OrderView,
  disruptions: DisruptionView,
}
</script>

<template>
  <div class="min-h-screen flex transition-colors duration-300"
       :class="isDarkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'">

    <div class="flex-1 min-w-0">
      <component
        :is="views[currentView]"
        :is-dark-mode="isDarkMode"
        @toggle-theme="toggleDarkMode"
      />
    </div>

    <aside class="w-56 border-l p-4 flex flex-col gap-4 transition-colors duration-300"
           :class="isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-white'">

      <h2 class="text-sm font-semibold tracking-wide mb-2"
          :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
        Navigation
      </h2>

      <button
        @click="currentView = 'orders'"
        class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all"
        :class="[
            currentView === 'orders'
            ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
            : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
        ]"
      >
        Orders
      </button>

      <button
        @click="currentView = 'disruptions'"
        class="w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all"
        :class="[
            currentView === 'disruptions'
            ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700'
            : (isDarkMode ? 'border-gray-700 bg-gray-800 hover:bg-gray-700 text-slate-200' : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700')
        ]"
      >
        Disruptions
      </button>

      <div class="mt-auto pt-4 border-t" :class="isDarkMode ? 'border-gray-700' : 'border-slate-200'">
        <button @click="toggleDarkMode" class="text-xs flex items-center gap-2"
           :class="isDarkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-black'">
           <span>{{ isDarkMode ? 'Mode: Dark' : 'Mode: Light' }}</span>
        </button>
      </div>

    </aside>
  </div>
</template>