<template>
  <div class="bg-white rounded-xl shadow-md border border-gray-100 p-6">
    <div class="flex items-center space-x-4">
      <div class="relative flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Example: Generate leads for retail startups in California interested in AI"
          class="block w-full pl-5 pr-12 py-4 text-base rounded-lg border border-gray-300 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
          @keyup.enter="handleSearch"
          :disabled="isLoading"
        />
      </div>
      <button
        @click="handleSearch"
        :disabled="isLoading"
        class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-medium rounded-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50"
      >
        {{ isLoading ? 'Searching...' : 'Search' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['search'])
const searchQuery = ref('')

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  emit('search', searchQuery.value)
}
</script>