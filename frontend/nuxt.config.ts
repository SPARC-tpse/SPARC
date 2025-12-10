// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    runtimeConfig: {
    public: {
      apiBaseUrl: "http://127.0.0.1:8000/api"   // <-- your base URL here
    }
  },
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  ssr: false,
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {}
    }
  }

})
