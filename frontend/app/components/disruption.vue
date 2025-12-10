<script setup lang="js">
import '../assets/css/tailwind.css'
import { ref } from 'vue'

const tab = ref('new')

const resources = ref([])
const types = ref([])


const newDisruption = ref({
    name: '',
    start: '',
    end: '',
    resource: null,
    type: null,
})

function setNow(field) {
    const now = new Date()
    const pad = n => String(n).padStart(2, '0')

    const formatted =
        `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`

    newDisruption.value[field] = formatted
}

async function loadDropdownData() {
    resources.value = await fetch("http://localhost:8000/api/resources/")
        .then(r => r.json())

    types.value = await fetch("http://localhost:8000/api/disruption-types/")
        .then(r => r.json())
}

loadDropdownData()

</script>


<template>
    <div class="min-h-screen bg-slate-950 text-slate-100">
        <header
            class="flex items-center justify-between border-b border-gray-600 px-6 py-4 bg-gradient-to-r from-indigo-900 via-slate-900 to-pink-900">
            <div class="font-semibold tracking-[0.12em] uppercase text-white">SPARC MES · Disruptions</div>
            <div class="flex gap-2">
                <button
                    class="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-slate-100 hover:border-pink-700"
                    @click="resetForm">
                    Reset
                </button>
                <button class="rounded-lg px-3 py-2 text-sm font-semibold text-white disabled:opacity-40"
                    :class="canSubmit ? 'bg-gradient-to-r from-indigo-500 to-pink-500' : 'bg-gray-800'"
                    :disabled="!canSubmit" @click="submitOrder">
                    Create
                </button>
            </div>
        </header>

        <main class="max-w-5xl mx-auto p-6 space-y-6">
            <div class="inline-flex rounded-xl bg-gray-800 p-1 border border-gray-800 shadow-lg shadow-black">
                <button class="px-4 py-2 text-sm font-semibold rounded-lg"
                    :class="tab === 'new' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : 'text-slate-200 hover:text-white'"
                    @click="tab = 'new'">
                    New
                </button>
                <button class="px-4 py-2 text-sm font-semibold rounded-lg"
                    :class="tab === 'overview' ? 'bg-gradient-to-r from-indigo-500 to-pink-900 text-white shadow' : 'text-slate-200 hover:text-white'"
                    @click="tab = 'overview'">
                    Overview
                </button>
            </div>

            <section v-if="tab === 'new'" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <label class="flex flex-col gap-1 text-sm text-slate-300">
                        Name
                        <input v-model="newDisruption.name" class="input" />
                    </label>

                    <label class="flex flex-col gap-1 text-sm text-slate-300">
                        ID (auto)
                        <input :value="formId" class="input bg-gray-800 text-slate-400" disabled />
                    </label>

                    <div class="mb-4">
                        <label class="text-sm text-slate-300">Start date</label>
                        <div class="flex gap-2">
                            <input v-model="newDisruption.start" type="datetime-local" class="input" />
                            <button type="button" @click="setNow('start')"
                                class="bg-blue-500 text-white px-3 rounded hover:bg-blue-600">Now</button>
                        </div>
                    </div>

                    <div class="mb-4">
                        <label class="text-sm text-slate-300">End date</label>
                        <div class="flex gap-2">
                            <input v-model="newDisruption.end" type="datetime-local" class="input" />
                            <button type="button" @click="setNow('end')"
                                class="bg-blue-500 text-white px-3 rounded hover:bg-blue-600">Now</button>
                        </div>
                    </div>
                    <label class="flex flex-col gap-1 text-sm text-slate-300">
                        Resource
                        <select v-model="newDisruption.resource"
                            class="input bg-gray-900 border-gray-700 text-white rounded-lg">
                            <option disabled value="">-- choose resource --</option>
                            <option v-for="r in resources" :key="r.id" :value="r.id">
                                {{ r.name }}
                            </option>
                        </select>
                    </label>
                    <label class="flex flex-col gap-1 text-sm text-slate-300">
                        Type
                        <select v-model="newDisruption.type"
                            class="input bg-gray-900 border-gray-700 text-white rounded-lg">
                            <option disabled value="">-- choose type --</option>
                            <option v-for="t in types" :key="t.id" :value="t.id">
                                {{ t.name }}
                            </option>
                        </select>
                    </label>

                </div>
            </section>
        </main>
    </div>
</template>