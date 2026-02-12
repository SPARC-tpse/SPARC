<script setup lang="js">
import { ref, computed } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRouter } from '#app'

definePageMeta({
    layout: 'custom'
})

const { isDarkMode } = useTheme();
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;
const router = useRouter();

const workerName = ref('');

const canSubmit = computed(() => {
    return workerName.value.length > 1;
})

function resetForm() {
    workerName.value = '';
}

async function submitWorker() {
    if (!canSubmit.value) return;

    try {
        await $fetch(`${API_BASE_URL}/api/worker/post`, {
            method: 'POST',
            body: { name: workerName.value }
        });


        await router.push('/worker/overview');

    } catch (error) {
        console.error('API Error:', error);
        alert('Failed to create worker');
    }
}
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar
          title="Workers · New"
          :can-submit="canSubmit"
          :show-reset="true"
          :show-create="true"
          create-label="Create"
          @reset="resetForm"
          @submit="submitWorker"
        />

        <main class="max-w-xl mx-auto p-6 space-y-4">
            <div class="rounded-xl border p-6 space-y-4 shadow-lg transition-colors"
                 :class="isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-white'">

                <h3 class="font-semibold text-lg">Add New Worker</h3>

                <label class="flex flex-col gap-1 text-sm label-text">
                    Worker Name
                    <input
                        v-model="workerName"
                        class="input"
                        placeholder="Max Musti"
                        autofocus
                        @keyup.enter="submitWorker"
                    />
                </label>

                <div class="pt-2 text-xs opacity-60">
                    This name will appear in the selection list when creating or editing orders.
                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
    .input {
        @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
    }
    .dark-mode .input {
        @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
    }
    .light-mode .input {
        @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
    }
    .dark-mode .label-text { @apply text-slate-300; }
    .light-mode .label-text { @apply text-slate-600; }
</style>