<script setup lang="js">
import { ref, computed, watch, onMounted } from 'vue'
import { useTheme } from '~/composables/useTheme'
import { useRoute, useRuntimeConfig, navigateTo } from '#app'
import WorkerMultiSelect from '~/components/WorkerMultiSelect.vue'

definePageMeta({ layout: 'custom' })

const { isDarkMode } = useTheme();
const route = useRoute();
const orderId = Number(route.params.id);
const config = useRuntimeConfig();
const API_BASE_URL = config.public.apiBaseUrl;

const order = ref({
    id: orderId, name: null, target_amount: null, start_date: null,
    end_date: null, product_name: null, priority: 'Medium', status: 'Planned', comments: '',
});

const selectedProcessStep = ref(null);
const processSteps = ref([]);
const bomFiles = ref([]);
const generalFiles = ref([]);
const allWorkers = ref([]);

const canSubmit = computed(() => {
    const o = order.value
    return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
})

const hasWarning = (field) => {
    const value = order.value[field]
    return value === null || value === undefined || value === ''
}

const hasProcessWarning = (step) => {
    const hasWorkers = step.workers && step.workers.length > 0;
    const hasResource = step.resource || step.resource_name;
    return !hasWorkers || !hasResource;
}

const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High' };
const statusMap = { 1: 'Planned', 2: 'Running', 3: 'Paused', 4: 'Done' };
const priorityMapReverse = { 'Low': 1, 'Medium': 2, 'High': 3 };
const statusMapReverse = { 'Planned': 1, 'Running': 2, 'Paused': 3, 'Done': 4 };

watch(selectedProcessStep, (newStep) => {
    if (newStep) console.log('Selected process step:', newStep)
})

function deleteStep(index) {
    if (selectedProcessStep.value === processSteps.value[index]) {
        selectedProcessStep.value = null;
    }
    processSteps.value.splice(index, 1);
}

function handleBomFilesUploaded(files) { bomFiles.value = files }
function handleGeneralFilesUploaded(files) { generalFiles.value = files }

function addStep() {
    processSteps.value.push({ _id: Date.now() + Math.random(), workers: [], resource: '', name: '' })
}

function updateResource(step, value) {
    step.resource_name = value;
}

async function updateOrder() {
    if (!canSubmit.value) return

    const processPayload = processSteps.value.map(step => {
        let resourceName = '';
        if (step.resource && typeof step.resource === 'object') {
            resourceName = step.resource.name;
        } else {
            resourceName = step.resource_name || step.resource || '';
        }
        return {
            name: step.name,
            resource: resourceName,
            workers: step.workers.map(w => w.name)
        };
    });

    const updatedOrder = {
        ...order.value,
        target_amount: Number(order.value.target_amount),
        priority: priorityMapReverse[order.value.priority] || 1,
        status: statusMapReverse[order.value.status] || 1,
        process: processPayload
    }

    try {
        await $fetch(`${API_BASE_URL}/api/order/put/${orderId}`, {
            method: 'PUT',
            body: updatedOrder
        })
        await navigateTo('/order/overview')
    } catch (error) {
        console.error('API Error:', error)
        alert('Update failed')
    }
}

function cancelEdit() { navigateTo('/order/overview') }
function handleTimeSaved(data) { console.log('Time saved:', data) }

function createDisruption() {
    if (!selectedProcessStep.value?.id) {
        alert('Please select a process step first')
        return
    }
    navigateTo(`/disruption/new?process=${selectedProcessStep.value.id}`)
}

async function loadAllWorkers() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/worker/list`, { method: 'GET' })
        allWorkers.value = response || []
    } catch (e) { console.error("Error loading workers", e) }
}

async function loadOrder() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/order/get/${orderId}`, { method: 'GET' })

        order.value = {
            ...response,
            priority: priorityMap[response.priority] || 'Low',
            status: statusMap[response.status] || 'Planned'
        };

        if (!response.processes || !Array.isArray(response.processes)) {
            processSteps.value = [];
            return;
        }

        processSteps.value = response.processes.map(item => ({
            _id: item.id,
            id: item.id,
            name: item.name,
            setup_time_seconds: item.setup_time_seconds || 0,
            waiting_time_seconds: item.waiting_time_seconds || 0,
            process_time_seconds: item.process_time_seconds || 0,
            workers: item.workers.map(w => ({ id: w.id, name: w.name })),
            resource: item.resource,
            resource_name: item.resource ? item.resource.name : ''
        }));
    } catch (error) { console.error('API Error:', error) }
}

onMounted(() => {
    loadOrder()
    loadAllWorkers()
})
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar title="Orders · Edit" :can-submit="canSubmit" :show-reset="true" :show-create="true" create-label="Update" @reset="cancelEdit" @submit="updateOrder" />

        <main class="max-w-5xl mx-auto p-6 space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2"><span>Name</span><span v-if="hasWarning('name')" class="text-amber-500">⚠️</span></div>
                    <input v-model="order.name" class="input" :class="hasWarning('name') ? 'border-amber-500' : ''" />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    ID <input :value="order.id" class="input disabled-input" disabled />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    Target amount <input v-model="order.target_amount" type="number" class="input" />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    Product name <input v-model="order.product_name" class="input" />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    Start date <input v-model="order.start_date" type="date" class="input" />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    End date <input v-model="order.end_date" type="date" class="input" />
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    Status
                    <select v-model="order.status" class="input">
                        <option value="Planned">Planned</option>
                        <option value="Running">Running</option>
                        <option value="Paused">Paused</option>
                        <option value="Done">Done</option>
                    </select>
                </label>
                <label class="flex flex-col gap-1 text-sm label-text">
                    Priority
                    <select v-model="order.priority" class="input">
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                    </select>
                </label>
                <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
                    Comments <textarea v-model="order.comments" rows="3" class="input" />
                </label>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="rounded-xl border p-4 shadow-lg transition-colors" :class="isDarkMode ? 'border-gray-900 bg-slate-900' : 'border-slate-200 bg-white'">
                    <FileUpload file-type="bom" label="Bill of Materials" :order-id="orderId" @files-uploaded="handleBomFilesUploaded" />
                </div>
                <div class="rounded-xl border p-4 shadow-lg transition-colors" :class="isDarkMode ? 'border-gray-900 bg-slate-900' : 'border-slate-200 bg-white'">
                    <FileUpload file-type="general" label="Additional Files" :order-id="orderId" @files-uploaded="handleGeneralFilesUploaded" />
                </div>
            </div>

            <div v-if="processSteps.length > 0" class="rounded-xl border p-4 space-y-4 shadow-lg transition-colors" :class="isDarkMode ? 'border-gray-900 bg-slate-900' : 'border-slate-200 bg-white'">
                <h3 class="font-semibold text-lg">Process Step Management</h3>
                <div>
                    <label class="flex flex-col gap-1 text-sm label-text">
                        Select Process Step
                        <select v-model="selectedProcessStep" class="input">
                            <option :value="null" disabled>-- Select a process step --</option>
                            <option v-for="(step, index) in processSteps" :key="step._id || index" :value="step">
                                <span v-if="hasProcessWarning(step)">⚠️ </span>
                                Step {{ index + 1 }}: {{ step.name || 'Unnamed' }}
                            </option>
                        </select>
                    </label>
                </div>

                <div v-if="selectedProcessStep" class="space-y-4 pt-4 border-t" :class="isDarkMode ? 'border-gray-700' : 'border-slate-200'">
                    <div v-if="selectedProcessStep.workers && selectedProcessStep.workers.length > 0">
                        <span class="text-sm label-text">Assigned:</span>
                        <span class="ml-2 font-semibold" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">
                            {{ selectedProcessStep.workers.map(w => w.name).join(', ') }}
                        </span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <ProcessTimer label="Setup Time" :initial-seconds="selectedProcessStep.setup_time_seconds" :process-id="selectedProcessStep.id" timer-type="setup_time" @time-saved="handleTimeSaved" />
                        <ProcessTimer label="Waiting Time" :initial-seconds="selectedProcessStep.waiting_time_seconds" :process-id="selectedProcessStep.id" timer-type="waiting_time" @time-saved="handleTimeSaved" />
                        <ProcessTimer label="Process Time" :initial-seconds="selectedProcessStep.process_time_seconds" :process-id="selectedProcessStep.id" timer-type="process_time" @time-saved="handleTimeSaved" />
                    </div>
                    <div>
                        <button @click="createDisruption" class="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-amber-500 to-red-500 shadow-md">⚠️ Create Disruption</button>
                    </div>
                </div>
            </div>

            <div class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors" :class="isDarkMode ? 'border-gray-900 bg-slate-900' : 'border-slate-200 bg-white'">
                <div class="flex items-center justify-between">
                    <h3 class="font-semibold">Process steps</h3>
                    <button class="text-sm hover:underline" :class="isDarkMode ? 'text-pink-200' : 'text-pink-600'" @click="addStep">+ Add step</button>
                </div>

                <div class="space-y-2">
                    <div v-if="processSteps.length > 0" class="grid grid-cols-[30px_30px_1fr_1fr_1fr] gap-2 text-xs px-1" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                        <span></span><span>#</span><span>Worker</span><span>Resource</span><span>Name</span>
                    </div>

                    <div v-for="(step, i) in processSteps" :key="step._id" class="grid grid-cols-[30px_30px_1fr_1fr_1fr] gap-2 items-start rounded-lg border p-2 transition-colors" :class="[isDarkMode ? 'border-gray-700 bg-gray-700' : 'border-slate-200 bg-slate-50', hasProcessWarning(step) ? 'border-amber-500' : '']">
                        <button @click="deleteStep(i)" class="flex items-center justify-center w-6 h-6 mt-1.5 rounded hover:bg-red-500/20 text-slate-400 hover:text-red-500" title="Delete step">✕</button>

                        <span class="text-xs text-center mt-2" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ i + 1 }}</span>

                        <div class="w-full">
                            <WorkerMultiSelect v-model="step.workers" :all-workers="allWorkers" />
                        </div>

                        <input :value="step.resource?.name || step.resource_name || ''" @input="updateResource(step, $event.target.value)" class="input h-10" placeholder="Resource" />
                        <input v-model="step.name" class="input h-10" placeholder="Name" />
                    </div>

                    <div v-if="processSteps.length === 0" class="text-center py-4 text-sm opacity-50">
                        No steps defined. Add a step to begin.
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
.input { @apply w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors; }
.dark-mode .input { @apply border-gray-700 bg-gray-800 text-slate-100 placeholder-slate-500 focus:border-pink-500; }
.light-mode .input { @apply border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:border-indigo-500; }
.dark-mode .disabled-input { @apply bg-gray-900 text-slate-500; }
.light-mode .disabled-input { @apply bg-slate-100 text-slate-500; }
.dark-mode .label-text { @apply text-slate-300; }
.light-mode .label-text { @apply text-slate-600; }
</style>