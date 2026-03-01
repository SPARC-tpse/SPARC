<script setup lang="js">
    import { ref } from 'vue'
    import { useTheme } from '~/composables/useTheme'

    const props = defineProps({
        fileType: {
            type: String,
            default: 'general' // 'bom' or 'general'
        },
        label: {
            type: String,
            default: 'Upload Files'
        },
        orderId: {
            type: Number,
            required: false
        }
    })

    const emit = defineEmits(['filesUpdated','filesUploaded', 'fileDeleted'])

    const { isDarkMode } = useTheme()
    const config = useRuntimeConfig()
    const API_BASE_URL = config.public.apiBaseUrl

    const uploadedFiles = ref([])
    const uploading = ref(false)
    const fileInput = ref(null)

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes'
        const k = 1024
        const sizes = ['Bytes', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    // Open file picker
    function openFilePicker() {
        fileInput.value?.click()
    }

    // Handle file selection
    async function handleFileSelect(event) {
        // can not be called without orderId because the uploaded file needs to know who its owner is
        if (props.orderId === undefined) return

        const files = event.target.files
        if (!files || files.length === 0) return

        uploading.value = true

        for (let file of files) {
            await uploadFile(file)
        }

        uploading.value = false
        event.target.value = '' // Reset input
    }

    // Upload a single file
    async function uploadFile(file) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('type', props.fileType)
        formData.append('order_id', props.orderId)

        try {
            const response = await $fetch(`${API_BASE_URL}/api/order/file/post/`, {
                method: 'POST',
                body: formData
            })

            uploadedFiles.value.push(response)
            emit('filesUpdated', uploadedFiles.value)
            console.log('File uploaded:', response)
        } catch (error) {
            console.error('Upload failed:', error)
            alert(`Failed to upload ${file.name}`)
        }
    }

    // Delete a file
    async function deleteFile(file, index) {
        if (!confirm(`Delete ${file.file_name}?`)) return

        try {
            await $fetch(`${API_BASE_URL}/api/order/file/delete/${file.id}/`, {
                method: 'DELETE'
            })

            uploadedFiles.value.splice(index, 1)
            emit('filesUpdated', uploadedFiles.value)
            console.log('File deleted:', file.file_name)
        } catch (error) {
            console.error('Delete failed:', error)
            alert(`Failed to delete ${file.file_name}`)
        }
    }

    // Load existing files for this order
    async function loadFiles() {
        if (props.orderId === undefined) return

        try {
            const response = await $fetch(`${API_BASE_URL}/api/order/file/get/${props.orderId}/`, {
                method: 'GET'
            })

            // Filter by file type
            uploadedFiles.value = response.files.filter(f => f.file_type === props.fileType)
            emit('filesUpdated', uploadedFiles.value)
        } catch (error) {
            console.error('Failed to load files:', error)
        }
    }

    onMounted(() => {
        loadFiles()
    })
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <label class="text-sm font-medium label-text">
        {{ label }}
      </label>
      <button
        @click="openFilePicker"
        :disabled="uploading"
        class="px-3 py-1.5 text-xs rounded-lg border transition-colors font-medium"
        :class="[
          uploading ? 'opacity-50 cursor-not-allowed' : '',
          isDarkMode
            ? 'border-gray-700 bg-gray-800 text-slate-200 hover:bg-gray-700'
            : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
        ]"
      >
        {{ uploading ? 'Uploading...' : '+ Add Files' }}
      </button>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      @change="handleFileSelect"
      class="hidden"
      accept="*/*"
    />

    <!-- File list -->
    <div
      v-if="uploadedFiles.length > 0"
      class="space-y-2"
    >
      <div
        v-for="(file, index) in uploadedFiles"
        :key="file.path"
        class="flex items-center justify-between p-3 rounded-lg border text-sm transition-colors"
        :class="isDarkMode
          ? 'border-gray-700 bg-gray-800'
          : 'border-slate-200 bg-slate-50'"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <!-- File icon -->
          <div class="text-2xl shrink-0">
            📄
          </div>

          <!-- File info -->
          <div class="flex-1 min-w-0">
            <div class="font-medium truncate" :class="isDarkMode ? 'text-slate-200' : 'text-slate-700'">
              {{ file.filename }}
            </div>
            <div class="text-xs" :class="isDarkMode ? 'text-slate-400' : 'text-slate-500'">
              {{ formatFileSize(file.size) }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <a
            :href="file.url"
            target="_blank"
            class="px-2 py-1 text-xs rounded border transition-colors"
            :class="isDarkMode
              ? 'border-gray-600 text-slate-300 hover:bg-gray-700'
              : 'border-slate-300 text-slate-600 hover:bg-slate-100'"
          >
            View
          </a>
          <button
            @click="deleteFile(file, index)"
            class="px-2 py-1 text-xs rounded border transition-colors"
            :class="isDarkMode
              ? 'border-red-900 text-red-400 hover:bg-red-900/30'
              : 'border-red-200 text-red-600 hover:bg-red-50'"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else
      class="p-4 rounded-lg border-2 border-dashed text-center"
      :class="isDarkMode
        ? 'border-gray-700 text-slate-400'
        : 'border-slate-300 text-slate-500'"
    >
      <p class="text-sm">No files uploaded yet</p>
    </div>
  </div>
</template>

<style scoped>
.label-text {
  @apply text-slate-300;
}
.light-mode .label-text {
  @apply text-slate-600;
}
</style>