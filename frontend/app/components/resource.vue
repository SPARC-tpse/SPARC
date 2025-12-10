<script setup lang="js">
import '../assets/css/tailwind.css'
import { ref, computed, onMounted } from 'vue'
import axios from "axios"

const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const props = defineProps(['isDarkMode'])
const emit = defineEmits(['toggle-theme'])

const tab = ref('new')
const newResource = ref({ name: "", type: "", status: "" })
const canSubmit = computed(() => newResource.value.name && newResource.value.type)

const resources = ref([])
const types = ref([])

function resetForm() {
    newResource.value = { name: '', type: '', status: '' }
}
async function submitResource() {
    if (!canSubmit.value) return;

    const payload = {
        name: newResource.value.name,
        type: Number(newResource.value.type),
        status: newResource.value.status,
    };
    try {
        const response = await axios.post(`${API_BASE_URL}/resource/create/`, payload);
        console.log("Created:", response.data);
        resetForm();
        await fetchResources();
    } catch (error) {
        console.error("Error creating resource:", error.response?.data || error);
    }
}

async function fetchDropdownData() {
    try {
        const [typesResponse] = await Promise.all([
            axios.get(`${API_BASE_URL}/resource-types/`),
        ]);

        types.value = typesResponse.data;

    } catch (error) {
        console.error("Error loading dropdown data:", error);
    }
}
async function fetchResources() {
    try {
        const response = await axios.get(`${API_BASE_URL}/resources/`);
        resources.value = response.data;
    } catch (error) {
        console.error("Error loading resources:", error);
    }
}
onMounted(() => {
    fetchDropdownData();
    fetchResources();
});
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <header class="flex items-center justify-between border-b px-6 py-4 transition-colors duration-300" :class="isDarkMode
            ? 'border-gray-600 bg-gradient-to-r from-indigo-900 via-slate-900 to-pink-900'
            : 'border-slate-200 bg-white text-slate-800 shadow-sm'">
            <div class="font-semibold tracking-[0.12em] uppercase"
                :class="isDarkMode ? 'text-white' : 'text-indigo-900'">
                SPARC MES · Resources
            </div>

            <div class="flex gap-2 items-center">
                <button @click="$emit('toggle-theme')"
                    class="mr-2 rounded-full p-2 hover:bg-opacity-20 hover:bg-gray-500 transition">
                    <span v-if="isDarkMode">🌙</span><span v-else>☀️</span>
                </button>
                <button class="rounded-lg border px-3 py-2 text-sm transition-colors"
                    :class="isDarkMode ? 'border-gray-700 bg-gray-900 text-slate-100 hover:border-pink-700' : 'border-slate-300 bg-white text-slate-700 hover:border-indigo-500 hover:text-indigo-600'"
                    @click="resetForm">Reset</button>
                <button
                    class="rounded-lg px-3 py-2 text-sm font-semibold text-white disabled:opacity-40 transition-all shadow-md"
                    :class="canSubmit ? 'bg-gradient-to-r from-indigo-500 to-pink-500' : 'bg-gray-500'"
                    :disabled="!canSubmit" @click="submitOrder">Create</button>

            </div>
        </header>

        <main class="max-w-5xl mx-auto p-6 space-y-6">
            <div class="inline-flex rounded-xl p-1 border shadow-lg transition-colors"
                :class="isDarkMode ? 'bg-gray-800 border-gray-800 shadow-black' : 'bg-white border-slate-200 shadow-slate-200'">
                <button class="px-4 py-2 text-sm font-semibold rounded-lg transition-all"
                    :class="tab === 'new' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : (isDarkMode ? 'text-slate-200 hover:text-white' : 'text-slate-500 hover:text-indigo-600')"
                    @click="tab = 'new'">New</button>
                <button class="px-4 py-2 text-sm font-semibold rounded-lg transition-all"
                    :class="tab === 'overview' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : (isDarkMode ? 'text-slate-200 hover:text-white' : 'text-slate-500 hover:text-indigo-600')"
                    @click="tab = 'overview'">Overview</button>
            </div>

            <!--"new" tab-->
            <section v-if="tab === 'new'" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <label class="flex flex-col gap-1 text-sm label-text">Name <input v-model="newResource.name"
                            class="input" /></label>
                    <label class="flex flex-col gap-1 text-sm label-text">Type
                        <select v-model="newResource.type" class="input">
                            <option disabled value="">-- choose --</option>
                            <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
                        </select>
                    </label>
                    <label class="flex flex-col gap-1 text-sm label-text">Status <input v-model="newResource.status"
                            class="input" /></label>
                </div>
            </section>

            <!--"overview" tab-->
            <section v-if="tab === 'overview'" class="space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="font-semibold">Resource overview</h3>
                    <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">
                        {{ resources.length }} total
                    </span>
                </div>
                <div class="grid gap-2">
                    <div class="grid grid-cols-[1.5fr,1fr,1fr] gap-2 text-xs"
                        :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                        <span>Name</span>
                        <span>Type</span>
                        <span>Status</span>
                    </div>
                    <div v-for="r in resources" :key="r.id"
                        class="grid grid-cols-[1.5fr,1fr,1fr] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
                        :class="isDarkMode
                            ? 'border-gray-700 bg-gray-700'
                            : 'border-slate-200 bg-slate-50 hover:bg-slate-100'">
                        <span class="font-medium">{{ r.name }}</span>
                        <span>
                            <span class="px-2 py-1 rounded-full text-xs font-semibold">
                                {{ r.resource_type_name }} </span>
                        </span>

                        <span>
                            <span class="px-2 py-1 rounded-full text-xs font-semibold">
                                {{ r.status }} </span>
                        </span>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<style scoped>
/* Gleiche Styles wie order.vue */
.input {
    @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors;
}

.dark-mode .input {
    @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500 focus:ring-1 focus:ring-pink-500;
}

.light-mode .input {
    @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500;
}

.dark-mode .disabled-input {
    @apply bg-gray-900 text-slate-500;
}

.light-mode .disabled-input {
    @apply bg-slate-100 text-slate-500;
}

.dark-mode .label-text {
    @apply text-slate-300;
}

.light-mode .label-text {
    @apply text-slate-600;
}
</style>