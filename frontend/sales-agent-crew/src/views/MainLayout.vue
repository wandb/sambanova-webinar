<template>
  <div class="h-screen flex">
    <!-- Sidebar -->
    <Sidebar ref="sidebarRef" @loadSearch="handleLoadSearch" class="h-screen flex-shrink-0" />
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">
      <!-- Fixed Header -->
      <Header @keysUpdated="onKeysUpdated" class="flex-shrink-0" />
      
      <!-- Scrollable Content -->
      <main class="flex-1 overflow-auto">
        <div class="container mx-auto px-4 py-8">
          <div class="max-w-4xl mx-auto">
            <!-- Search Section (Fixed) -->
            <div class="sticky top-0 z-10 bg-gray-50 pt-4 pb-2">
              <SearchSection 
                :keys-updated="keysUpdated"
                :isLoading="isLoading"
                @search="handleSearch" 
                @openSettings="openSettings"
              />
            </div>

            <!-- Scrollable Results -->
            <div class="mt-4">
              <!-- Loading Progress Bar -->
              <div v-if="isLoading" class="mt-8">
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                      <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
                      <h3 class="text-lg font-semibold text-gray-900">{{ currentLoadingMessage }}</h3>
                    </div>
                    <span class="text-sm text-gray-500">Please wait</span>
                  </div>

                  <div class="w-full bg-primary-600 h-2 rounded-full animate-pulse"></div>
                  
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
                <CompanyResultCard 
                  v-for="(result, index) in results" 
                  :key="index" 
                  :company="result" 
                />
              </div>

              <!-- No Results Message -->
              <div v-if="!isLoading && results.length === 0" class="mt-8">
                <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
                  <p class="text-gray-600">No results found. Try modifying your search query.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Completion Summary -->
      <SearchNotification
        :show="showCompletion"
        :time="(executionTime / 1000).toFixed(1)"
        :result-count="results.length"
      />
    </div>
  </div>

  <!-- Settings Modal -->
  <SettingsModal ref="settingsModalRef" />
</template>

<script setup>
import { ref, onUnmounted, computed } from 'vue'
import Header from '../components/Header.vue'
import SearchSection from '../components/SearchSection.vue'
import SearchNotification from '../components/SearchNotification.vue'
import Sidebar from '../components/Sidebar.vue'
import { generateLeads } from '../services/api'
import SettingsModal from '../components/SettingsModal.vue'
import CompanyResultCard from '../components/CompanyResultCard.vue'
import { useAuth } from '@clerk/vue'

const results = ref([])
const expandedItems = ref({})
const copySuccess = ref({})
const isLoading = ref(false)
const currentLoadingMessage = ref('')
const showCompletion = ref(false)
const executionTime = ref(0)
const searchStartTime = ref(0)
let loadingInterval
const sidebarRef = ref(null)
const errorMessage = ref('')
const settingsModalRef = ref(null)
const { userId } = useAuth()

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
  }, 2000)
}

const stopLoadingMessages = () => {
  clearInterval(loadingInterval)
  currentLoadingMessage.value = ''
}

const handleSearch = async (query) => {
  isLoading.value = true
  errorMessage.value = ''
  searchStartTime.value = Date.now()
  startLoadingMessages()
  
  try {
    const keys = settingsModalRef.value?.getKeys()
    const sambanovaKey = keys?.sambanovaKey
    const exaKey = keys?.exaKey

    if (!sambanovaKey || !exaKey) {
      throw new Error('Missing API keys')
    }

    const searchResults = await generateLeads(query, { sambanovaKey, exaKey })
    results.value = searchResults
    
    // Calculate execution time
    executionTime.value = Date.now() - searchStartTime.value
    
    // Show completion notification
    showCompletion.value = true
    setTimeout(() => {
      showCompletion.value = false
    }, 3000)

    // Save to search history
    // Get the current expanded state for all results
    const expandedState = Object.fromEntries(
      searchResults.map((_, index) => [index, expandedItems.value[index] || false])
    )
    
    // Add to sidebar history
    sidebarRef.value?.addSearch(query, searchResults, expandedState)

  } catch (error) {
    console.error('Search error:', error)
    errorMessage.value = error.message || 'An error occurred during search'
  } finally {
    isLoading.value = false
    stopLoadingMessages()
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

// Update handleLoadSearch to restore expanded state
const handleLoadSearch = (search) => {
  results.value = search.results
  expandedItems.value = search.expandedState || 
    Object.fromEntries(search.results.map((_, index) => [index, false]))
  
  // Scroll to top of results
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const getKeys = () => {
  // Now using localStorage
  const sambanovaKey = localStorage.getItem(`sambanova_key_${userId}`)
  const exaKey = localStorage.getItem(`exa_key_${userId}`)
  return { sambanovaKey, exaKey }
}

onUnmounted(() => {
  stopLoadingMessages()
})

// **Line 22**: Define the reactive keysUpdated variable
const keysUpdated = ref(0)

// **Line 50**: Handle the keysUpdated event
const onKeysUpdated = () => {
  keysUpdated.value = Date.now()
}
</script>
