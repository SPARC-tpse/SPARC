// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  //css: ['~/assets/css/tailwind.css'],
  ssr: false,
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {}
    }
  },
  runtimeConfig: {
    public: {
      // Keep base host only; frontend pages already append `/api/...`.
      apiBaseUrl: (process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000')
        .replace(/\/api\/?$/, '')
        .replace(/\/$/, '')
    }
  }
})
