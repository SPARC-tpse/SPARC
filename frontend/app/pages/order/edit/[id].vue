<script setup lang="js">
    import { ref, computed } from 'vue'
    import { useTheme } from '~/composables/useTheme'

    definePageMeta({
        layout: 'custom'
    })

    const { isDarkMode } = useTheme();
    const route = useRoute();
    const orderId = Number(route.params.id);
    const config = useRuntimeConfig();
    const API_BASE_URL = config.public.apiBaseUrl;
    const order = ref({
        id: orderId,
        name: null,
        target_amount: null,
        start_date: null,
        end_date: null,
        product_name: null,
        priority: null,
        status: null,
        comments: '',
    });
    //const steps = ref([{ worker: '', resource: '', name: '' }]);
    const selectedProcessStep = ref(null);
    const processSteps = ref([]);
    const isLoadingOrder = ref(true);
    const bomFiles = ref([]);
    const generalFiles = ref([]);
    const canSubmit = computed(() => {
        const o = order.value
        return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
    })
    const hasWarning = (field) => {
        const value = order.value[field]
        return value === null || value === undefined || value === ''
    }
    const hasProcessWarning = (step) => {
        return !step.workers || !step.resource || step.workers.length === 0
    }
    watch(selectedProcessStep, (newStep) => {
        if (newStep) {
            console.log('Selected process step:', newStep)
        }
    })

    function deleteStep(index) {
        // TODO: make api call

        processSteps.value.splice(index, 1);
        if (selectedProcessStep.value === processSteps.value[index]) {
            selectedProcessStep.value = null;
        }
    }

    function handleBomFilesUploaded(files) {
      bomFiles.value = files
      console.log('BOM files updated:', files)
    }

    function handleGeneralFilesUploaded(files) {
      generalFiles.value = files
      console.log('General files updated:', files)
    }

    function addStep() {
        processSteps.value.push({ worker: '', resource: '', name: '' })
    }

    async function updateOrder() {
        /*
        if (!canSubmit.value) return

        //const processSteps = steps.value.filter(step => step.worker || step.resource || step.name)
        const updatedOrder = {
            ...order.value,
            target_amount: Number(order.value.target_amount),
            process: processSteps
        }

        console.log('Updating order:', updatedOrder)

        try {
          const response = await $fetch(`${API_BASE_URL}/api/order/put/${orderId}`, {
            method: 'PUT',
            body: updatedOrder
          })
          // Navigate back to overview
          await navigateTo('/order/overview')
          //return response
        } catch (error) {
          console.error('API Error:', error)
          alert(error)
        }
        */
    }

    function cancelEdit() {
        navigateTo('/order/overview')
    }

    function handleTimeSaved(data) {
        console.log('Time saved:', data)
        // Optionally refresh the order data to get updated times
    }

    function createDisruption() {
        if (!selectedProcessStep.value || !selectedProcessStep.value.id) {
            alert('Please select a process step first')
            return
        }

        // Navigate to disruption creation with process ID parameter
        navigateTo(`/disruption/new?process=${selectedProcessStep.value.id}`)
    }

    async function loadOrder() {
        try {
            const response = await $fetch(`${API_BASE_URL}/api/order/get/${orderId}`, {
                method: 'GET'
            })
            order.value = response;

            if (!response.processes || !Array.isArray(response.processes)) {
                console.warn("No processes found in response");
                return;
            }

            processSteps.value = response.processes.map(item => ({
                id: item.id,
                name: item.name,
                setup_time_seconds: item.setup_time_seconds || 0,
                waiting_time_seconds: item.waiting_time_seconds || 0,
                process_time_seconds: item.process_time_seconds || 0,
                workers: item.workers.map(w => ({ id: w.id, name: w.name })),
                resource: {
                    id: item.resource.id,
                    name: item.resource.name,
                    type: {
                        id: item.resource.type.id,
                        name: item.resource.type.name
                    },
                    status: item.resource.status
                }
            }));

            console.log(processSteps.value)
        } catch (error) {
            console.error('API Error:', error)
            alert('Failed to load order')
        }
    }

    onMounted(() => {
        loadOrder()
    })
</script>

<template>
    <div :class="isDarkMode ? 'dark-mode' : 'light-mode'">
        <Topbar
            title="Orders · Edit"
            :can-submit="canSubmit"
            :show-reset="true"
            :show-create="true"
            create-label="Update"
            @reset="cancelEdit"
            @submit="updateOrder"
        />

        <main class="max-w-5xl mx-auto p-6 space-y-4">
            <!-- Order Details -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <!-- Name -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Name</span>
                        <span v-if="hasWarning('name')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <input
                        v-model="order.name"
                        class="input"
                        :class="hasWarning('name') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    />
                </label>

                <!-- ID -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    ID
                    <input :value="order.id" class="input disabled-input" disabled />
                </label>

                <!-- Target Amount -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Target amount</span>
                        <span v-if="hasWarning('target_amount')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <input
                        v-model="order.target_amount"
                        type="number"
                        class="input"
                        :class="hasWarning('target_amount') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    />
                </label>

                <!-- Product Name -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Product name</span>
                        <span v-if="hasWarning('product_name')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <input
                        v-model="order.product_name"
                        class="input"
                        :class="hasWarning('product_name') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    />
                </label>

                <!-- Start Date -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Start date</span>
                        <span v-if="hasWarning('start_date')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <input
                        v-model="order.start_date"
                        type="date"
                        inputmode="numeric"
                        class="input"
                        :class="hasWarning('start_date') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    />
                </label>

                <!-- End Date -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>End date</span>
                        <span v-if="hasWarning('end_date')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <input
                        v-model="order.end_date"
                        type="date"
                        inputmode="numeric"
                        class="input"
                        :class="hasWarning('end_date') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    />
                </label>

                <!-- Status -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Status</span>
                        <span v-if="hasWarning('status')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <select
                        v-model="order.status"
                        :value="order.status"
                        class="input"
                        :class="hasWarning('status') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    >
                        <option :value="null" disabled>-- Select status --</option>
                        <option value=1>Planned</option>
                        <option value=2>Running</option>
                        <option value=3>Paused</option>
                        <option value=4>Done</option>
                    </select>
                </label>

                <!-- Priority -->
                <label class="flex flex-col gap-1 text-sm label-text">
                    <div class="flex items-center gap-2">
                        <span>Priority</span>
                        <span v-if="hasWarning('priority')" class="text-amber-500" title="Missing value">⚠️</span>
                    </div>
                    <select
                        v-model="order.priority"
                        :value="order.priority"
                        class="input"
                        :class="hasWarning('priority') ? 'border-amber-500 ring-1 ring-amber-500' : ''"
                    >
                        <option :value="null" disabled>-- Select priority --</option>
                        <option value=1>High</option>
                        <option value=2>Medium</option>
                        <option value=3>Low</option>
                    </select>
                </label>

                <!-- Comments (no warning) -->
                <label class="flex flex-col gap-1 text-sm label-text sm:col-span-2">
                    Comments
                    <textarea v-model="order.comments" rows="3" class="input" />
                </label>
            </div>

            <!-- file uploads -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- bom upload -->
                <div
                    class="rounded-xl border p-4 shadow-lg transition-colors"
                    :class="isDarkMode
                        ? 'border-gray-900 bg-slate-900 shadow-black'
                        : 'border-slate-200 bg-white shadow-slate-200'"
                >
                    <FileUpload
                        file-type="bom"
                        label="Bill of Materials"
                        :order-id="orderId"
                        @files-uploaded="handleBomFilesUploaded"
                        @file-deleted="handleBomFilesUploaded"
                    />
                </div>

                <!-- general files upload-->
                <div
                    class="rounded-xl border p-4 shadow-lg transition-colors"
                    :class="isDarkMode
                        ? 'border-gray-900 bg-slate-900 shadow-black'
                        : 'border-slate-200 bg-white shadow-slate-200'"
                >
                    <FileUpload
                        file-type="general"
                        label="Additional Files"
                        :order-id="orderId"
                        @files-uploaded="handleGeneralFilesUploaded"
                        @file-deleted="handleGeneralFilesUploaded"
                    />
                </div>
            </div>

            <!-- Process Step Selector -->
            <div
                v-if="processSteps && processSteps.length > 0"
                class="rounded-xl border p-4 space-y-4 shadow-lg transition-colors"
                :class="isDarkMode
                ? 'border-gray-900 bg-slate-900 shadow-black'
                : 'border-slate-200 bg-white shadow-slate-200'"
            >
                <h3 class="font-semibold text-lg">Process Step Management</h3>

                <!-- Process Step Dropdown -->
                <div>
                    <label class="flex flex-col gap-1 text-sm label-text">
                        Select Process Step
                        <select
                            v-model="selectedProcessStep"
                            class="input"
                        >
                            <option :value="null" disabled>-- Select a process step --</option>
                            <option
                                v-for="(step, index) in processSteps"
                                :key="step.id || index"
                                :value="step"
                            >
                                <span v-if="hasProcessWarning(step)">⚠️ </span>
                                Step {{ index + 1 }}: {{ step.name || 'Unnamed' }} - {{ step.resource?.name || 'No resource' }}
                            </option>
                        </select>
                    </label>
                </div>

                <!-- Process Step Details -->
                <div
                    v-if="selectedProcessStep"
                    class="space-y-4 pt-4 border-t"
                    :class="isDarkMode
                        ? 'border-gray-700'
                        : 'border-slate-200'"
                >
                    <!-- Process Step ID -->
                    <div>
                        <span class="text-sm label-text">Process Step ID:</span>
                        <span class="ml-2 font-mono font-semibold"
                        :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">
                        {{ selectedProcessStep.id || 'N/A' }}
                        </span>
                    </div>

                    <!-- Workers Display -->
                    <div v-if="selectedProcessStep.workers && selectedProcessStep.workers.length > 0">
                        <span class="text-sm label-text">Workers:</span>
                        <span
                            class="ml-2 font-semibold"
                            :class="isDarkMode
                                ? 'text-slate-200'
                                : 'text-slate-700'"
                        >
                            {{ selectedProcessStep.workers.map(w => w.name).join(', ') }}
                        </span>
                    </div>

                    <!-- Resource Display -->
                    <div v-if="selectedProcessStep.resource">
                        <span class="text-sm label-text">Resource:</span>
                        <span class="ml-2 font-semibold"
                            :class="isDarkMode
                                ? 'text-slate-200'
                                : 'text-slate-700'"
                        >
                            {{ selectedProcessStep.resource.name }} ({{ selectedProcessStep.resource.type.name }})
                        </span>
                    </div>

                    <!-- Setup Time Timer -->
                    <ProcessTimer
                        label="Setup Time"
                        :initial-seconds="selectedProcessStep.setup_time_seconds || 0"
                        :process-id="selectedProcessStep.id"
                        timer-type="setup_time"
                        @time-saved="handleTimeSaved"
                    />

                    <!-- Create Disruption Button -->
                    <div>
                        <button
                            @click="createDisruption"
                            class="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all shadow-md bg-gradient-to-r from-amber-500 to-red-500 hover:shadow-lg"
                        >
                            ⚠️ Create Disruption
                        </button>
                    </div>

                    <!-- Waiting Time Timer -->
                    <ProcessTimer
                        label="Waiting Time"
                        :initial-seconds="selectedProcessStep.waiting_time_seconds || 0"
                        :process-id="selectedProcessStep.id"
                        timer-type="waiting_time"
                        @time-saved="handleTimeSaved"
                    />

                    <!-- Process Time Timer -->
                    <ProcessTimer
                        label="Process Time"
                        :initial-seconds="selectedProcessStep.process_time_seconds || 0"
                        :process-id="selectedProcessStep.id"
                        timer-type="process_time"
                        @time-saved="handleTimeSaved"
                    />
                </div>

                <!-- No process step selected message -->
                <div
                    v-else
                    class="p-4 rounded-lg border-2 border-dashed text-center"
                    :class="isDarkMode
                    ? 'border-gray-700 text-slate-400'
                    : 'border-slate-300 text-slate-500'"
                >
                    <p class="text-sm">Please select a process step to manage timing</p>
                </div>
            </div>

            <!-- No process steps message -->
            <div
                v-else
                class="rounded-xl border p-4 text-center transition-colors"
                :class="isDarkMode
                ? 'border-gray-900 bg-slate-900'
                : 'border-slate-200 bg-white'"
            >
                <p class="text-sm" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                    No process steps defined for this order. Add process steps below to enable timing management.
                </p>
            </div>

            <!-- Process steps editor -->
            <div
                class="rounded-xl border p-4 space-y-3 shadow-lg transition-colors"
                :class="isDarkMode
                    ? 'border-gray-900 bg-slate-900 shadow-black'
                    : 'border-slate-200 bg-white shadow-slate-200'"
            >
                <div class="flex items-center justify-between">
                    <h3 class="font-semibold">Process steps</h3>
                    <button
                    class="text-sm hover:underline"
                    :class="isDarkMode ? 'text-pink-200 hover:text-pink-100' : 'text-pink-600 hover:text-pink-800'"
                    @click="addStep"
                    >+ Add step</button>
                </div>
                <div class="space-y-2">
                    <div class="grid grid-cols-[30px,30px,1fr,1fr,1fr] gap-2 text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
                        <span>#</span>
                        <span></span>
                        <span>Workers</span>
                        <span>Resource</span>
                        <span>Name</span>
                    </div>
                    <div
                        v-for="(step, i) in processSteps"
                        :key="step.id || i"
                        class="grid grid-cols-[30px,30px,1fr,1fr,1fr] gap-2 items-center rounded-lg border p-2 transition-colors"
                        :class="[
                        isDarkMode ? 'border-gray-700 bg-gray-700' : 'border-slate-200 bg-slate-50',
                        hasProcessWarning(step) ? 'border-amber-500' : ''
                        ]"
                    >
                        <span class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">{{ i + 1 }}</span>
                        <span v-if="hasProcessWarning(step)" class="text-amber-500 text-sm" title="Missing worker or resource">⚠️</span>
                        <span v-else class="text-sm"></span>
                        <input
                            :value="step.workers?.map(w => w.name).join(', ') || ''"
                            @input="updateWorkers(step, $event.target.value)"
                            class="input h-10"
                            :class="!step.workers || step.workers.length === 0 ? 'border-amber-500' : ''"
                            placeholder="Required (comma-separated)"
                        />
                        <input
                            :value="step.resource?.name || ''"
                            @input="updateResource(step, $event.target.value)"
                            class="input h-10"
                            :class="!step.resource ? 'border-amber-500' : ''"
                            placeholder="Required"
                        />
                        <input
                            v-model="step.name"
                            class="input h-10"
                            placeholder="Optional"
                        />
                        <button
                            class="px-2 py-1 text-xs rounded border transition-colors"
                            :class="isDarkMode
                                ? 'border-rose-500/70 text-rose-200 hover:bg-rose-500/10'
                                : 'border-rose-200 text-rose-600 hover:bg-rose-50'"
                            @click="deleteStep(i)"
                        >
                            Delete
                        </button>
                    </div>
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
