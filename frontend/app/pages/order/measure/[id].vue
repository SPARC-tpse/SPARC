<script setup lang="js">
    import { ref, onMounted } from 'vue'
    import { useTheme } from '~/composables/useTheme'

    const { isDarkMode } = useTheme()
    const route = useRoute()
    const orderId = route.params.id
    const order = ref({
        id: orderId,
        name: '',
        start_date: '',
        end_date: '',
        target_amount: '',
        product_name: '',
        status: 'Planned',
        priority: 'Medium',
        comments: ''
    })
    const steps = ref([{ worker: '', resource: '', notes: '' }])

    async function loadOrder() {
        const config = useRuntimeConfig();
        const API_BASE_URL = config.public.apiBaseUrl;
        const ENDPOINT = '/api/orders/get/'

        try {
            const response = await $fetch(`${API_BASE_URL}${ENDPOINT}${orderId}`, {
                method: 'GET'
            })
            console.log("response data:" + response)
            console.log(response)
            order.value = response
            steps.value = response.process || [{ worker: '', resource: '', notes: '' }]
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
            title="Orders · Measure"
            :show-reset="false"
            :show-create="false"
        />

        <label class="flex flex-col gap-1 text-sm label-text">
          Process Step
          <select v-model="newOrder.priority" class="input">
            <option>Step 1</option>
            <option>Step 2</option>
            <option>Step 3</option>
          </select>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
            Set-up Time
            <button>start/stop</button>
            <button>reset</button>
            01:00 result
            00:30 best time for this machine type
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
            Disruption Time
            <button>start/stop</button>
            <button>reset</button>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
            Waiting Time
            <button>start/stop</button>
            <button>reset</button>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
            Process Time
            <button>start/stop</button>
            <button>reset</button>
        </label>

        <label class="flex flex-col gap-1 text-sm label-text">
            Quantity
            <button>+</button>
            <button>-</button>
        </label>
    </div>
</template>