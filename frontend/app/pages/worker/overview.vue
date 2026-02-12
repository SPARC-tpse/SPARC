<script setup lang="js">
    import { ref, onMounted } from 'vue'
    import { useTheme } from '~/composables/useTheme'

    definePageMeta({
        layout: 'custom'
    })

    const { isDarkMode } = useTheme();
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;

    const workers = ref([]);

    // STATE LOGIC
    const isDeleteMode = ref(false)
    const deleteConfirmId = ref(null)

    //Delete Mode Toggle
    function toggleDeleteMode() {
        isDeleteMode.value = !isDeleteMode.value
        deleteConfirmId.value = null
    }


    //Row Button Logic
    function handleRowAction(id) {
        if (!isDeleteMode.value) {
            //Edit Mode
            navigateTo(`/worker/edit/${id}`)
        } else {
            //Delete Mode Toggle
            if (deleteConfirmId.value === id) {
                deleteConfirmId.value = null
            } else {
                deleteConfirmId.value = id
            }
        }
    }

    //Actual deletion
    async function executeDelete(id) {
        console.log(`Deleting Worker ${id}`)
        try {
            await $fetch(`${API_BASE_URL}/api/worker/delete/${id}`, {
                method: 'DELETE'
            })
            // Optimistic update
            workers.value = workers.value.filter(o => o.id !== id)
            deleteConfirmId.value = null
        } catch (error) {
            console.error('API Error:', error)
            alert('Failed to delete worker')
        }
    }

    async function loadWorker() {
        try {

            const response = await $fetch(`${API_BASE_URL}/api/worker/list`, {
                method: 'GET'
            })
            workers.value = response || []
        } catch (error) {
            console.error('API Error:', error)
        }
    }

    onMounted(() => {
        loadWorker()
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
                                isDeleteMode
                                    ? 'bg-slate-200 text-slate-800 border-slate-300'
                                    : 'bg-white text-slate-700 border-slate-200 hover:border-red-400 hover:text-red-600',
                                isDarkMode && isDeleteMode ? '!bg-slate-700 !text-white !border-slate-600' : '',
                                isDarkMode && !isDeleteMode ? '!bg-slate-800 !text-slate-200 !border-slate-700 hover:!border-red-500 hover:!text-red-400' : ''
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

                <div class="grid gap-2">
                    <div class="grid grid-cols-[1.5fr,1fr,120px] gap-2 text-xs px-3" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                        <span>Name</span><span>ID</span><span class="text-center">Action</span>
                    </div>

                    <div
                        v-for="worker in workers"
                        :key="worker.id"
                        class="grid grid-cols-[1.5fr,1fr,120px] gap-2 items-center rounded-lg border p-3 text-sm transition-colors"
                        :class="[
                            isDarkMode ? 'border-gray-700 bg-slate-900' : 'border-slate-200 bg-slate-50 hover:bg-slate-100',
                            deleteConfirmId === worker.id && !isDarkMode ? 'bg-red-50 border-red-100' : '',
                            deleteConfirmId === worker.id && isDarkMode ? 'bg-red-900/10 border-red-900/30' : ''
                        ]"
                    >
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

                        <span class="font-mono text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">#{{ worker.id }}</span>

                        <button
                            @click="handleRowAction(worker.id)"
                            class="px-2 py-1.5 text-xs rounded border transition-colors w-full text-center"
                            :class="[
                                !isDeleteMode && isDarkMode ? 'border-gray-600 text-slate-400 hover:bg-slate-800' : '',
                                !isDeleteMode && !isDarkMode ? 'border-slate-300 text-slate-600 hover:bg-white' : '',
                                isDeleteMode && deleteConfirmId === worker.id ? 'border-slate-400 text-slate-500 hover:bg-slate-200' : '',
                                isDeleteMode && deleteConfirmId !== worker.id ? 'border-red-200 text-red-500 hover:bg-red-50 hover:border-red-300' : ''
                            ]"
                        >
                            {{ !isDeleteMode ? 'Edit' : (deleteConfirmId === worker.id ? 'Cancel' : 'Delete') }}
                        </button>
                    </div>

                    <div v-if="workers.length === 0" class="text-center py-8 text-sm opacity-50">
                        No workers found.
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<style scoped>
    .dark-mode { @apply bg-slate-950 text-slate-100; }
    .light-mode { @apply bg-slate-50 text-slate-900; }
</style>