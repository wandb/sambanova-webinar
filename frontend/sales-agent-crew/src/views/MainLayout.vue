<template>
  <div class="h-screen flex">
    <!-- Sidebar -->
    <Sidebar ref="sidebarRef" @loadSearch="handleLoadSearch" class="h-screen flex-shrink-0" />
    
    <!-- Main Content -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">
      <!-- Fixed Header -->
      <Header ref="headerRef" @keysUpdated="onKeysUpdated" class="flex-shrink-0" />
      
      <!-- Scrollable Content -->
      <main class="flex-1 overflow-auto">
        <div class="container mx-auto px-4 py-8">
          <div class="max-w-4xl mx-auto">
            <!-- Search Section (Fixed) -->
            <div class="sticky top-0 z-10 bg-gray-50 pt-4 pb-2">
              <SearchSection 
                :keysUpdated="keysUpdateCounter"
                @searchStarted="handleSearchStart"
                @searchComplete="handleSearchComplete"
                @searchError="handleSearchError"
                @openSettings="openSettingsModal"
              />
            </div>

            <!-- Loading State -->
            <div v-if="isLoading && !results" class="mt-8">
              <!-- Generate Sales Loading -->
              <div v-if="searchType === 'generate_sales'" class="space-y-4">
                <LoadingSpinner message="Searching for companies..." v-if="loadingStep === 1" />
                <LoadingSpinner message="Analyzing company data..." v-if="loadingStep === 2" />
                <LoadingSpinner message="Generating sales opportunities..." v-if="loadingStep === 3" />
                <LoadingSpinner message="Creating personalized outreach..." v-if="loadingStep === 4" />
              </div>
              
              <!-- Research Report Loading -->
              <div v-if="searchType === 'research_report'" class="space-y-4">
                <LoadingSpinner message="Planning research content..." v-if="loadingStep === 1" />
                <LoadingSpinner message="Gathering industry data..." v-if="loadingStep === 2" />
                <LoadingSpinner message="Analyzing market trends..." v-if="loadingStep === 3" />
                <LoadingSpinner message="Writing research report..." v-if="loadingStep === 4" />
              </div>
            </div>

            <!-- Results Section -->
            <div v-if="results" class="mt-8">
              <!-- Research Report -->
              <ResearchReport
                v-if="currentSearchType === 'educational_content'"
                :report="results"
                @showFullReport="showFullReportModal = true"
              />
              
              <!-- Sales Leads -->
              <div v-else-if="currentSearchType === 'sales_leads'" class="space-y-4">
                <CompanyResultCard
                  v-for="(company, index) in results.companies"
                  :key="index"
                  :company="company"
                />
              </div>
            </div>

            <!-- No Results Message -->
            <div v-if="!isLoading && results.length === 0" class="mt-8">
              <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 text-center">
                <p class="text-gray-600">No results found. Try modifying your search query.</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Completion Summary -->
      <SearchNotification
        :show="showCompletion"
        :time="(executionTime / 1000).toFixed(1)"
        :result-count="resultsCount"
      />
    </div>
  </div>

  <!-- Settings Modal -->
  <SettingsModal ref="settingsModalRef" />

  <!-- Error Modal -->
  <ErrorModal 
    :show="showError"
    :error-message="errorMessage"
    @close="showError = false"
  />

  <!-- Full Report Modal -->
  <FullReportModal
    v-if="showFullReportModal"
    :isOpen="showFullReportModal"
    :report="currentReport"
    @close="showFullReportModal = false"
  />
</template>

<script setup>
import { ref, onUnmounted, computed, onMounted, watch } from 'vue'
import Header from '../components/Header.vue'
import SearchSection from '../components/SearchSection.vue'
import SearchNotification from '../components/SearchNotification.vue'
import Sidebar from '../components/Sidebar.vue'
import { generateLeads, generateResearch, generateOutreach } from '../services/api'
import SettingsModal from '../components/SettingsModal.vue'
import CompanyResultCard from '../components/CompanyResultCard.vue'
import { useAuth } from '@clerk/vue'
import ResearchReport from '../components/ResearchReport.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorModal from '../components/ErrorModal.vue'
import FullReportModal from '../components/FullReportModal.vue'
import axios from 'axios'

// Rename to "results" so we match the template usage
const results = ref({
  companies: [],
  report: null
})
const expandedItems = ref({})
const copySuccess = ref({})
const isLoading = ref(false)
const currentLoadingMessage = ref('')
const showCompletion = ref(false)
const executionTime = ref(0)
const searchStartTime = ref(0)
let loadingInterval = null
const sidebarRef = ref(null)
const errorMessage = ref('')
const settingsModalRef = ref(null)
const { userId, isSignedIn } = useAuth()
const headerRef = ref(null)
const currentSearchType = ref(null)
const showFullReportModal = ref(false)
const showNotification = ref(false)
const searchTime = ref('')
const showError = ref(false)
const keysUpdateCounter = ref(0)
const loadingStep = ref(0)
const searchType = ref(null)
const currentReport = ref(null)

// Example loading messages
const loadingMessages = [
  'Fetching company details',
  'Analyzing market trends',
  'Preparing outreach emails'
]

const handleSearchComplete = ({ results: newResults, type }) => {
  console.log('[MainLayout] handleSearchComplete => type:', type)
  console.log('[MainLayout] newResults:', newResults)
  
  // Clear any existing loading interval
  if (loadingInterval) {
    clearInterval(loadingInterval)
    loadingInterval = null
  }
  
  isLoading.value = false
  loadingStep.value = 0
  
  // Safely handle null results
  if (newResults) {
    results.value = newResults
    console.log('[MainLayout] results updated:', results.value)
  } else {
    results.value = {
      companies: [],
      report: null
    }
  }
}

const handleSearchStart = async (type) => {
  console.log('[MainLayout] handleSearchStart fired with type:', type)
  results.value = {
    companies: [],
    report: null
  }
  startLoadingMessages(type)
  searchType.value = type

  try {
    // Get API keys from localStorage
    const sambanovaKey = localStorage.getItem(`sambanova_key_${userId}`)
    const serperKey = localStorage.getItem(`serper_key_${userId}`)
    const exaKey = localStorage.getItem(`exa_key_${userId}`)

    // Decrypt keys if they exist
    const decryptedSambanovaKey = sambanovaKey ? await decryptKey(sambanovaKey) : null
    const decryptedSerperKey = serperKey ? await decryptKey(serperKey) : null
    const decryptedExaKey = exaKey ? await decryptKey(exaKey) : null

    if (!decryptedSambanovaKey) {
      throw new Error('SambaNova API key is required')
    }

    // Make API request with headers
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/query`, 
      { query: searchQuery.value },
      {
        headers: {
          'Content-Type': 'application/json',
          'x-sambanova-key': decryptedSambanovaKey,
          'x-serper-key': decryptedSerperKey || '',
          'x-exa-key': decryptedExaKey || ''
        }
      }
    )

    console.log('[MainLayout] API Response:', response.data)
    results.value = response.data
    isLoading.value = false
    clearInterval(loadingInterval)

  } catch (error) {
    console.error('[MainLayout] Error:', error)
    isLoading.value = false
    clearInterval(loadingInterval)
    
    // Show error modal with specific message
    const errorMessage = error.response?.data?.error || error.message || 'An unexpected error occurred'
    showError(errorMessage)
  }
}

const startLoadingMessages = (type) => {
  console.log('[MainLayout] startLoadingMessages with type:', type)
  isLoading.value = true
  searchType.value = type
  loadingStep.value = 1
  
  // Clear any existing interval
  if (loadingInterval) {
    clearInterval(loadingInterval)
  }
  
  // Start new loading interval
  loadingInterval = setInterval(() => {
    if (loadingStep.value < 4) {
      loadingStep.value++
    } else {
      clearInterval(loadingInterval)
    }
  }, 3000)
}

// Clean up interval on component unmount
onUnmounted(() => {
  if (loadingInterval) {
    clearInterval(loadingInterval)
  }
})

// If search errors out
const handleSearchError = (error) => {
  console.log('[MainLayout] handleSearchError =>', error)
  isLoading.value = false
  errorMessage.value = error
  showError.value = true
}

// Possibly triggered from the sidebar
const handleLoadSearch = (searchItem) => {
  console.log('[MainLayout] handleLoadSearch =>', searchItem)
  // Do something with searchItem
}

// keysUpdated logic
const onKeysUpdated = () => {
  keysUpdateCounter.value++ // Increment counter to trigger reactivity
}

// For debugging results length
const resultsCount = computed(() => {
  // In a "sales_leads" scenario, results might be { companies: [ ... ] }
  if (Array.isArray(results.value?.companies)) {
    return results.value.companies.length
  }
  // If "educational_content," results might be an entire object with different shape
  return 0
})

// Optional: log to see changes
watch(
  () => results.value,
  (val) => {
    console.log('[MainLayout] results changed:', val)
  },
  { deep: true }
)

onMounted(() => {
  // Example: check if user is signed in
  if (!isSignedIn) {
    console.warn('[MainLayout] user not signed in')
    // Possibly redirect or show a sign-in screen
  }
})

const openSettingsModal = () => {
  headerRef.value.openSettings()
}

const openFullReport = (report) => {
  currentReport.value = report
  showFullReportModal.value = true
}

const closeFullReport = () => {
  showFullReportModal.value = false
  currentReport.value = null
}
</script>
