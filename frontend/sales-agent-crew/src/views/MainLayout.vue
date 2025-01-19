# MainLayout.vue
<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <!-- Search Section -->
        <SearchSection 
          :isLoading="isLoading"
          @search="handleSearch" 
        />

        <!-- Loading Progress Bar -->
        <!-- Loading Progress Bar -->
  <!-- Loading Progress Bar -->
    <div v-if="isLoading" class="mt-8">
      <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-3">
            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <h3 class="text-lg font-semibold text-gray-900">{{ currentLoadingMessage }}</h3>
          </div>
          <span class="text-sm text-gray-500">Please wait</span>
        </div>
        
        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div class="bg-blue-600 h-2 rounded-full animate-pulse"></div>
        </div>
        
        <div class="text-sm text-gray-500">
          <span>This may take a few moments</span>
        </div>
      </div>
    </div>

        <!-- Debug Info (hidden) -->
        <div class="hidden">
          isLoading: {{ isLoading }}
          results length: {{ results.length }}
        </div>

        <!-- Results Section -->
        <div v-if="!isLoading && results.length > 0" class="mt-8 space-y-4">
          <div v-for="(result, index) in results" :key="index" 
               class="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-lg overflow-hidden">
            <!-- Collapsible Header -->
            <div 
              @click="toggleExpand(index)"
              class="p-6 flex justify-between items-center cursor-pointer hover:bg-blue-600/50 transition-all duration-200"
            >
              <div class="flex-1">
                <h3 class="text-xl font-bold text-white mb-3">{{ result.company_name }}</h3>
                <div class="flex flex-wrap gap-6 text-white/90">
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    {{ result.headquarters }}
                  </div>
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    {{ result.website }}
                  </div>
                  <span class="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                    {{ result.funding_status }}
                  </span>
                </div>
              </div>
              <div class="flex items-center ml-4">
                <span class="mr-2 text-sm font-medium text-white/90">
                  {{ expandedItems[index] ? 'Show Less' : 'Show More' }}
                </span>
                <svg 
                  class="w-5 h-5 text-white/70 transform transition-transform duration-200"
                  :class="{ 'rotate-180': expandedItems[index] }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            <!-- Expanded Content -->
            <div v-if="expandedItems[index]" class="bg-white">
              <div class="p-6 space-y-4">
                <div class="flex items-center space-x-2">
                  <div class="p-2 bg-blue-100 rounded-lg">
                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h4 class="text-lg font-semibold text-gray-900">{{ result.email_subject }}</h4>
                </div>
                <div class="relative bg-gray-50 rounded-lg p-5">
                  <p class="text-gray-700 leading-relaxed pr-10">{{ result.email_body }}</p>
                  <button 
                    @click.stop="copyToClipboard(result.email_body, index)"
                    class="absolute top-4 right-4 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
                    :class="{ 'text-green-500 bg-green-50': copySuccess[index] }"
                  >
                    <svg v-if="!copySuccess[index]" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results Message -->
        <div v-if="!isLoading && results.length === 0" class="mt-8">
          <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
            <p class="text-gray-600">No results found. Try modifying your search query.</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '../components/Header.vue'
import SearchSection from '../components/SearchSection.vue'
import { onUnmounted } from 'vue'

const results = ref([])
const expandedItems = ref({})
const copySuccess = ref({})
const isLoading = ref(false)
const currentLoadingMessage = ref('')
let loadingInterval

const loadingMessages = [
  'Fetching company details',
  'Analyzing market trends',
  'Preparing outreach emails'
] 
const startLoadingMessages = () => {
  let index = 0
  currentLoadingMessage.value = loadingMessages[0]
  loadingInterval = setInterval(() => {
    index = (index + 1) % loadingMessages.length
    currentLoadingMessage.value = loadingMessages[index]
  }, 2000) // Change message every 2 seconds
}

const stopLoadingMessages = () => {
  clearInterval(loadingInterval)
  currentLoadingMessage.value = ''
}
const handleSearch = async (searchQuery) => {
  isLoading.value = true
  startLoadingMessages()
  try {
    console.log('Making API call with query:', searchQuery)
    const response = await fetch('http://localhost:8000/research', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ query: searchQuery })
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    console.log('API Response:', data)

    results.value = data
    console.log('Results after setting:', results.value)

    expandedItems.value = Object.fromEntries(
      data.map((_, index) => [index, false])
    )
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    stopLoadingMessages()
    isLoading.value = false
  }
}

const toggleExpand = (index) => {
  expandedItems.value[index] = !expandedItems.value[index]
}

const copyToClipboard = async (text, index) => {
  try {
    await navigator.clipboard.writeText(text)
    copySuccess.value[index] = true
    setTimeout(() => {
      copySuccess.value[index] = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}
onUnmounted(() => {
  stopLoadingMessages()
})
</script>