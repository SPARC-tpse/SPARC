<script setup lang="js">
import { ref, computed, watch, onMounted } from 'vue'
import WorkerMultiSelect from '~/components/WorkerMultiSelect.vue'

definePageMeta({ layout: 'custom' })

const { theme, getBadgeColor } = useAppTheme()
const route = useRoute()
const orderId = Number(route.params.id)
const config = useRuntimeConfig()
const API_BASE_URL = config.public.apiBaseUrl

//state
const order = ref({
    id: orderId, name: null, target_amount: null, start_date: null,
    end_date: null, product_name: null, priority: 'Medium', status: 'Planned', comments: '',
})

const selectedProcessStep = ref(null)
const processSteps = ref([])
const allWorkers = ref([])
const allResources = ref([])

//logic
const canSubmit = computed(() => {
    const o = order.value
    return Boolean(o.name && o.start_date && o.end_date && o.target_amount && o.product_name)
})

const hasWarning = (field) => !order.value[field]

const hasProcessWarning = (step) => {
    const hasWorkers = step.workers && step.workers.length > 0
    const hasResource = step.resource || step.resource_name
    return !hasWorkers || !hasResource
}

const priorityMap = { 1: 'Low', 2: 'Medium', 3: 'High' }
const statusMap = { 1: 'Planned', 2: 'Running', 3: 'Paused', 4: 'Done' }
const priorityMapReverse = { 'Low': 1, 'Medium': 2, 'High': 3 }
const statusMapReverse = { 'Planned': 1, 'Running': 2, 'Paused': 3, 'Done': 4 }

function addStep() {
    processSteps.value.push({ _id: Date.now() + Math.random(), workers: [], resource: '', name: '' })
}

function deleteStep(index) {
    if (selectedProcessStep.value === processSteps.value[index]) selectedProcessStep.value = null
    processSteps.value.splice(index, 1)
}

function updateResource(step, value) {
    step.resource_name = value
}

async function loadOrder() {
    try {
        const response = await $fetch(`${API_BASE_URL}/api/order/get/${orderId}`)

        order.value = {
            ...response,
            priority: priorityMap[response.priority] || 'Medium',
            status: statusMap[response.status] || 'Planned'
        }


        const rawSteps = response.processes || response.process || []
        processSteps.value = rawSteps.map(item => ({
            _id: item.id || Math.random(),
            id: item.id,
            name: item.name,
            setup_time_seconds: item.setup_time_seconds || 0,
            waiting_time_seconds: item.waiting_time_seconds || 0,
            process_time_seconds: item.process_time_seconds || 0,
            workers: item.workers ? item.workers.map(w => ({ id: w.id, name: w.name })) : [],
            resource: item.resource,
            resource_name: item.resource ? item.resource.name : ''
        }))
    } catch (error) {
        console.error('Error loading order:', error)
    }
}

async function loadDependencies() {
    try {
        const [workers, resources] = await Promise.all([
            $fetch(`${API_BASE_URL}/api/worker/list`),
            $fetch(`${API_BASE_URL}/api/resource/list`)
        ])
        allWorkers.value = workers || []
        allResources.value = resources || []
    } catch (e) { console.error("Error loading dependencies", e) }
}

async function updateOrder() {
    if (!canSubmit.value) return

    const processPayload = processSteps.value.map(step => ({
        name: step.name,
        resource: step.resource_name || (typeof step.resource === 'string' ? step.resource : step.resource?.name) || '',
        workers: step.workers.map(w => w.name)
    }))

    const payload = {
        ...order.value,
        target_amount: Number(order.value.target_amount),
        priority: priorityMapReverse[order.value.priority] || 1,
        status: statusMapReverse[order.value.status] || 1,
        process: processPayload
    }

    try {
        await $fetch(`${API_BASE_URL}/api/order/put/${orderId}`, { method: 'PUT', body: payload })
        navigateTo('/order/overview')
    } catch (error) { alert('Update failed') }
}

onMounted(() => {
    loadOrder()
    loadDependencies()
})
</script>

<template>
    <div :class="theme.pageWrapper">
        <Topbar title="Orders · Edit" :can-submit="canSubmit" :show-reset="true" create-label="Update" @reset="() => navigateTo('/order/overview')" @submit="updateOrder" />

        <main :class="theme.container" class="space-y-6">

            <section :class="theme.card">
                <div :class="theme.formGrid">
                    <label :class="theme.label">
                        <div class="flex items-center gap-2"><span>Order Name</span><span v-if="hasWarning('name')" class="text-amber-500">⚠️</span></div>
                        <input v-model="order.name" :class="[theme.input, hasWarning('name') ? 'border-amber-500' : '']" />
                    </label>
                    <label :class="theme.label">ID <input :value="order.id" :class="theme.inputDisabled" disabled /></label>
                    <label :class="theme.label">Target Amount <input v-model="order.target_amount" type="number" :class="theme.input" /></label>
                    <label :class="theme.label">Product Name <input v-model="order.product_name" :class="theme.input" /></label>
                    <label :class="theme.label">Start Date <input v-model="order.start_date" type="date" :class="theme.input" /></label>
                    <label :class="theme.label">End Date <input v-model="order.end_date" type="date" :class="theme.input" /></label>
                    <label :class="theme.label">Status
                        <select v-model="order.status" :class="theme.input">
                            <option v-for="s in ['Planned', 'Running', 'Paused', 'Done']" :key="s">{{s}}</option>
                        </select>
                    </label>
                    <label :class="theme.label">Priority
                        <select v-model="order.priority" :class="theme.input">
                            <option v-for="p in ['High', 'Medium', 'Low']" :key="p">{{p}}</option>
                        </select>
                    </label>
                    <label :class="theme.label" class="sm:col-span-2">Comments <textarea v-model="order.comments" rows="2" :class="theme.input" /></label>
                </div>
            </section>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div :class="theme.card"><FileUpload file-type="bom" label="Bill of Materials" :order-id="orderId" /></div>
                <div :class="theme.card"><FileUpload file-type="general" label="Additional Files" :order-id="orderId" /></div>
            </div>

            <section v-if="processSteps.length > 0" :class="theme.card">
                <h3 class="font-semibold text-lg">Live Step Management</h3>
                <label :class="theme.label">Select Step to edit times
                    <select v-model="selectedProcessStep" :class="theme.input">
                        <option :value="null">-- Choose a step --</option>
                        <option v-for="(step, index) in processSteps" :key="step._id" :value="step">
                            {{ hasProcessWarning(step) ? '⚠️ ' : '' }} Step {{ index + 1 }}: {{ step.name || 'Unnamed' }}
                        </option>
                    </select>
                </label>

                <div v-if="selectedProcessStep" class="pt-4 border-t border-slate-700/30 space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <ProcessTimer label="Setup" :initial-seconds="selectedProcessStep.setup_time_seconds" :process-id="selectedProcessStep.id" timer-type="setup_time" />
                        <ProcessTimer label="Waiting" :initial-seconds="selectedProcessStep.waiting_time_seconds" :process-id="selectedProcessStep.id" timer-type="waiting_time" />
                        <ProcessTimer label="Process" :initial-seconds="selectedProcessStep.process_time_seconds" :process-id="selectedProcessStep.id" timer-type="process_time" />
                    </div>
                    <button @click="navigateTo(`/disruption/new?process=${selectedProcessStep.id}`)" :class="theme.btnWarning">⚠️ Create Disruption</button>
                </div>
            </section>

            <section :class="theme.card">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="font-semibold text-lg">Process Steps Editor</h3>
                    <button :class="theme.linkAction" @click="addStep">+ Add step</button>
                </div>

                <div class="space-y-3">
                    <div v-if="processSteps.length > 0" :class="['px-1 opacity-70', theme.processStepGrid.replace('items-start', '')]">
                        <span></span><span class="text-center font-bold">#</span><span :class="theme.label">Worker</span><span :class="theme.label">Resource</span><span :class="theme.label">Step Name</span>
                    </div>

                    <div v-for="(step, i) in processSteps" :key="step._id" :class="[theme.processStepGrid, theme.row, hasProcessWarning(step) ? 'border-amber-500/50' : '']">
                        <button @click="deleteStep(i)" class="mt-2 text-slate-400 hover:text-red-500 transition-colors">✕</button>
                        <span class="mt-2 text-center text-xs opacity-50">{{ i + 1 }}</span>

                        <div class="w-full">
                            <WorkerMultiSelect v-model="step.workers" :all-workers="allWorkers" />
                        </div>

                        <select :value="step.resource?.name || step.resource_name || ''" @change="updateResource(step, $event.target.value)" :class="theme.input" class="mt-0 h-[38px]">
                            <option value="" disabled hidden>-- Resource --</option>
                            <option v-for="res in allResources" :key="res.id" :value="res.name">{{ res.name }}</option>
                        </select>

                        <input v-model="step.name" :class="theme.input" class="mt-0 h-[38px]" placeholder="Step Name" />
                    </div>

                    <div v-if="processSteps.length === 0" class="py-10 text-center opacity-50 italic">No steps defined. Add one to begin.</div>
                </div>
            </section>
        </main>
    </div>
</template>