<template>
  <div class="relative flex">
    <!-- Collapse Button -->
    <button 
      @click="isCollapsed = !isCollapsed"
      class="absolute -right-3 top-4 z-10 bg-white rounded-full p-1 shadow-md border border-gray-200"
    >
      <svg 
        class="w-4 h-4 text-gray-600 transform transition-transform"
        :class="{ 'rotate-180': isCollapsed }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- Sidebar Content -->
    <div 
      class="bg-white border-r border-gray-200 flex flex-col transition-all duration-300"
      :class="{ 'w-64': !isCollapsed, 'w-0': isCollapsed }"
    >
      <div class="p-4 border-b border-gray-200" v-show="!isCollapsed">
        <h2 class="text-lg font-semibold text-gray-900">Search History</h2>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4 space-y-2" v-show="!isCollapsed">
        <button
          v-for="(search, index) in searchHistory"
          :key="index"
          @click="loadSearch(search)"
          class="w-full text-left p-3 rounded-lg hover:bg-gray-100 transition-colors group"
        >
          <div class="text-sm font-medium text-gray-900 truncate">
            {{ search.query }}
          </div>
          <div class="text-xs text-gray-500 mt-1">
            {{ new Date(search.timestamp).toLocaleString() }}
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@clerk/vue'

const { userId } = useAuth()
const searchHistory = ref([])
const isCollapsed = ref(false)

const loadSearch = (search) => {
  emit('loadSearch', search)
}

// Load history from localStorage for the current user
onMounted(() => {
  const userHistory = localStorage.getItem(`search-history-${userId}`)
  if (userHistory) {
    searchHistory.value = JSON.parse(userHistory)
  }
})

const emit = defineEmits(['loadSearch'])

// Expose method to add new searches
defineExpose({
  addSearch: (query, results, expandedState) => {
    const newSearch = {
      query,
      results,
      expandedState,
      timestamp: Date.now()
    }
    searchHistory.value.unshift(newSearch)
    searchHistory.value = searchHistory.value.slice(0, 50)
    localStorage.setItem(
      `search-history-${userId}`, 
      JSON.stringify(searchHistory.value)
    )
  }
})
</script> 