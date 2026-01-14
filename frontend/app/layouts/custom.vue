<script setup lang="js">
import { useTheme } from '~/composables/useTheme'

// Get theme for background color
const { isDarkMode } = useTheme()
</script>

<template>
  <!-- Main container with flex layout -->
  <div class="min-h-screen flex transition-colors duration-300"
       :class="isDarkMode ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'">

    <!-- Left side: Page content (takes up remaining space) -->
    <div class="flex-1 min-w-0">
      <!-- This is where page content gets injected -->
      <slot />
    </div>

    <!-- Right side: Navigation Sidebar (fixed width) -->
    <Navbar />

  </div>
</template>