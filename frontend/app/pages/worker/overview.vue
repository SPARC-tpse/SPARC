<script setup lang="js">
    import { ref, onMounted } from 'vue'
    import { useTheme } from '~/composables/useTheme'
    // import { useWorkerWebSocket } from '~/composables/useWorkerWebSocket'

    definePageMeta({
        layout: 'custom'
    })

    const { isDarkMode } = useTheme();
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;

    const workers = ref([
        {
            id: 1,
            name: "Herbert"
        }
    ]);

    //STATE LOGIC
    const isDeleteMode = ref(false) // Default is false (so Edit Mode is default)
    const deleteConfirmId = ref(null)

    /*
    // Update automatically if changes in the database have been broadcasted via Websocket
    const handleOrderUpdate = async (data) => {
        // console.log('Worker update received:', data);

        if (data.action === 'created') {
            // Add new order to the list
            workers.value.push(data.data);
        } else if (data.action === 'updated') {
            // Update existing order
            const index = workers.value.findIndex(o => o.id === data.data.id);
            if (index !== -1) {
                workers.value[index] = data.data;
            }
        } else if (data.action === 'deleted') {
            // Remove order from list
            workers.value = workers.value.filter(o => o.id !== data.data.id);
        }
    }

    // Connect to WebSocket
    const { connected } = useOrderWebSocket(handleOrderUpdate)
    */

    // 1. Delete Mode Toggle (Top)
    function toggleDeleteMode() {
        isDeleteMode.value = !isDeleteMode.value
        // Close all open confirmations when toggling
        deleteConfirmId.value = null
    }

    // 2. Row Button Logic
    function handleRowAction(id) {
        if (!isDeleteMode.value) {
            // STANDARD: Edit Mode (Delete Mode is OFF)
            console.log(`Edit Order ${id}`)
            navigateTo(`/order/edit/${id}`)
        } else {
            // DELETE MODE (Delete Mode is ON)
            if (deleteConfirmId.value === id) {
                // Was already in Confirm status -> Cancel
                deleteConfirmId.value = null
            } else {
                // Starts the deletion process for this row
                deleteConfirmId.value = id
            }
        }
    }

    // 3. Actual deletion (Confirm button next to name)
    async function executeDelete(id) {
        console.log(`Deleting Worker ${id}`)
        try {
            const response = await $fetch(`${API_BASE_URL}/api/worker/delete/${id}`, {
                method: 'DELETE'
            })
            return response
        } catch (error) {
            console.error('API Error:', error)
            alert('Failed to delete order')
        }

        // TODO: refresh does not work for some reason
        workers.value = workers.value.filter(o => o.id !== id)
        deleteConfirmId.value = null
    }

    async function loadWorker() {
        try {
            const response = await $fetch(`${API_BASE_URL}/api/worker/get`, {
                method: 'GET'
            })
            console.log("response data:" + response)
            workers.value = response
        } catch (error) {
            console.error('API Error:', error)
            alert('Error: Problems when fetching workers')
            // throw error
        }
    }

    onMounted(async () => {
        await loadWorker()
    })
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar
          title="Workers · Overview"
          :show-reset="false"
          :show-create="false"
        />

        <main class="max-w-5xl mx-auto p-6 space-y-4">
            <section
                class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
                :class="isDarkMode
                    ? 'border-gray-700 bg-slate-900 shadow-black'
                    : 'border-slate-200 bg-white shadow-slate-200'"
            >
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <h3 class="font-semibold">Workers overview</h3>
                        <span class="text-xs" :class="isDarkMode ? 'text-slate-300' : 'text-slate-500'">{{ workers.length }} total</span>
                    </div>

                    <div class="flex gap-2">
                        <button
                            @click="toggleDeleteMode"
                            class="px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm"
                            :class="[
                                // If Delete Mode is ON -> Button looks 'pressed' or active
                                isDeleteMode
                                    ? 'bg-slate-200 text-slate-800 border-slate-300'
                                    : 'bg-white text-slate-700 border-slate-200 hover:border-red-400 hover:text-red-600',

                                // Dark Mode variants
                                isDarkMode && isDeleteMode ? 'bg-slate-700 text-white border-slate-600' : '',
                                isDarkMode && !isDeleteMode ? 'bg-slate-800 text-slate-200 border-slate-700 hover:border-red-500 hover:text-red-400' : ''
                            ]"
                        >
                            {{ isDeleteMode ? 'Done deleting' : 'Delete mode' }}
                        </button>

                        <NuxtLink
                          to="/worker/new"
                          class="px-3 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-indigo-500 to-pink-500 hover:shadow-lg"
                        >
                            + New Worker
                        </NuxtLink>
                    </div>
                </div>

                <!-- table -->
                <div class="grid gap-2">
                    <!-- first row with column names -->
                    <div class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,120px] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                        <span>Name</span><span>ID</span>
                    </div>

                    <!-- rows -->
                    <div
                        v-for="worker in workers"
                        :key="worker.id"
                        class="grid grid-cols-[1.5fr,1fr,1fr,1fr,1fr,0.8fr,120px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
                        :class="[
                            isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-slate-50 hover:bg-slate-100',
                            // Highlight row red if deletion needs confirmation
                            deleteConfirmId === worker.id && !isDarkMode ? 'bg-red-50 border-red-100' : '',
                            deleteConfirmId === worker.id && isDarkMode ? 'bg-red-900/10 border-red-900/30' : ''
                        ]"
                    >
                        <!-- name + delete confirm button -->
                        <span class="font-medium flex items-center gap-2 overflow-hidden">
                            <button
                                v-if="deleteConfirmId === worker.id"
                                @click="executeDelete(worker.id)"
                                class="bg-red-600 text-white text-[10px] px-2 py-1 rounded animate-pulse hover:bg-red-700 shrink-0 shadow-sm"
                            >
                                Confirm
                            </button>
                            <span class="truncate">{{ worker.name }}</span>
                        </span>

                        <!-- id -->
                        <span :class="isDarkMode ? 'text-slate-200' : 'text-slate-600'">{{ worker.id }}</span>

                        <button
                            @click="handleRowAction(worker.id)"
                            class="px-2 py-1 text-xs rounded border transition-colors w-full text-center"
                            :class="[
                                // 1. STANDARD: Edit Mode (Indigo/Blue) - If Delete Mode is OFF
                                !isDeleteMode && isDarkMode ? 'border-indigo-800 text-indigo-200 hover:bg-indigo-900' : '',
                                !isDeleteMode && !isDarkMode ? 'border-indigo-300 text-indigo-700 hover:bg-indigo-50' : '',

                                // 2. DELETE MODE: Cancel State (Gray) - If Delete Mode is ON AND row is currently being confirmed
                                isDeleteMode && deleteConfirmId === worker.id && isDarkMode ? 'border-slate-500 text-slate-400 hover:bg-slate-800' : '',
                                isDeleteMode && deleteConfirmId === worker.id && !isDarkMode ? 'border-slate-400 text-slate-600 hover:bg-slate-200' : '',

                                // 3. DELETE MODE: Init State (Red) - If Delete Mode is ON but row is still normal
                                isDeleteMode && deleteConfirmId !== worker.id && isDarkMode ? 'border-red-900 text-red-400 hover:bg-red-900/30' : '',
                                isDeleteMode && deleteConfirmId !== worker.id && !isDarkMode ? 'border-red-200 text-red-600 hover:bg-red-50' : ''
                            ]"
                        >
                            {{
                            !isDeleteMode
                              ? 'Edit'
                              : (deleteConfirmId === worker.id ? 'Cancel deletion' : 'Delete')
                            }}
                        </button>
                    </div>
                </div>
            </section>
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