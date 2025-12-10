<script setup lang="js">
import { ref } from 'vue'


import OrderView from './components/order.vue'
import DisruptionView from './components/disruption.vue'


const currentView = ref('orders')

const views = {
  orders: OrderView,
  disruptions: DisruptionView,
}
</script>

<template>
  <div class="min-h-screen flex bg-slate-950 text-slate-100">

    
    <div class="flex-1">
      <component :is="views[currentView]" />
    </div>

    
    <aside class="w-56 border-l border-gray-700 bg-slate-900 p-4 flex flex-col gap-4">

      <h2 class="text-sm font-semibold tracking-wide text-slate-300 mb-2">
        Navigation
      </h2>

      <button
        @click="currentView = 'orders'"
        class="w-full px-3 py-2 text-left rounded-lg border border-gray-700 bg-gray-800 hover:bg-gray-700 text-sm font-medium"
        :class="currentView === 'orders' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700' : ''"
      >
        Orders
      </button>

      <button
        @click="currentView = 'disruptions'"
        class="w-full px-3 py-2 text-left rounded-lg border border-gray-700 bg-gray-800 hover:bg-gray-700 text-sm font-medium"
        :class="currentView === 'disruptions' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white border-pink-700' : ''"
      >
        Disruptions
      </button>

    </aside>
  </div>
</template>

<style scoped>

</style>
