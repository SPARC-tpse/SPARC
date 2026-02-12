<script setup lang="js">
const { theme } = useAppTheme()
const { isDarkMode } = useTheme()
const route = useRoute()

// Hilfsfunktion für den aktiven Pfad
const isActive = (path) => route.path.startsWith(path)

// Zentralisierte Navigations-Links
const navLinks = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Orders', path: '/order' },
  { name: 'Disruptions', path: '/disruption' },
  { name: 'Resources', path: '/resource' },
  { name: 'Workers', path: '/worker' }
]
</script>

<template>
  <aside :class="theme.sidebar">
    
    <h2 :class="theme.navLabel">
      Navigation
    </h2>

    <nav class="flex flex-col gap-2">
      <NuxtLink
        v-for="link in navLinks"
        :key="link.path"
        :to="link.path === '/dashboard' ? link.path : `${link.path}/overview`"
        :class="isActive(link.path) ? theme.navLinkActive : theme.navLinkInactive"
      >
        {{ link.name }}
      </NuxtLink>
    </nav>

    <div :class="theme.navFooter">
      <div class="flex items-center gap-2">
        <div class="w-1.5 h-1.5 rounded-full" :class="isDarkMode ? 'bg-indigo-500' : 'bg-amber-500'"></div>
        <span>Mode: {{ isDarkMode ? 'Dark' : 'Light' }}</span>
      </div>
    </div>

  </aside>
</template>