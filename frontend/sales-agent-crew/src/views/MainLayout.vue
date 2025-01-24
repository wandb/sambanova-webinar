<template>
  <!-- Outer container uses flex-row so the sidebar and main area appear side-by-side -->
  <div class="min-h-screen flex">
    
    <!-- 1) SIDEBAR -->
    <Sidebar @selectReport="handleSavedReportSelect" />

    <!-- 2) MAIN COLUMN -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">

      <!-- PAGE HEADER -->
      <Header 
        @keysUpdated="handleKeysUpdated"
        ref="headerRef"
        class="flex-none"
      />

      <!-- MAIN CONTENT WRAPPER -->
      <main class="flex-grow flex flex-col p-4 space-y-4 overflow-y-auto">

        <!-- SearchSection: triggers search events, note :keysUpdated -->
        <SearchSection 
          :keysUpdated="keysUpdateCounter"
          :isLoading="isLoading"
          @searchStart="handleSearchStart"
          @searchComplete="handleSearchComplete"
          @searchError="handleSearchError"
          @openSettings="openSettings"
        />

        <!-- Our "Search Complete" toast notification -->
        <SearchNotification
          :show="showNotification"
          :time="searchTime"
          :resultCount="resultCount"
        />

        <!-- LOADING SPINNER: shown whenever isLoading is true -->
        <div v-if="isLoading" class="mt-8">
          <LoadingSpinner 
            :message="loadingMessage" 
            :subMessage="loadingSubMessage" 
          />
        </div>

        <!-- ERROR MODAL -->
        <ErrorModal
          :show="showError"
          :errorMessage="errorMessage"
          @close="showError = false"
        />

        <!-- RESULTS SECTION -->
        <div v-if="hasResults" class="mt-6 space-y-6">
          <div class="grid grid-cols-1 gap-6">
            <!-- Sales Leads Results -->
            <template v-if="queryType === 'sales_leads'">
              <CompanyResultCard 
                v-for="(result, index) in results.results" 
                :key="index"
                :company="result"
              />
            </template>

            <!-- Research / Educational Content Results -->
            <template v-else>
              <ResearchReport :report="results" />
            </template>
          </div>
        </div>

        <!-- FULL REPORT MODAL (if needed) -->
        <FullReportModal
          v-if="selectedReport"
          :open="reportModalOpen"
          :report-data="selectedReport"
          @close="reportModalOpen = false"
        />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import Header from '@/components/Header.vue'
import SearchSection from '@/components/SearchSection.vue'
import SearchNotification from '@/components/SearchNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import CompanyResultCard from '@/components/CompanyResultCard.vue'
import ResearchReport from '@/components/ResearchReport.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import FullReportModal from '@/components/FullReportModal.vue'
import { useReportStore } from '@/stores/reportStore'
import Sidebar from '@/components/Sidebar.vue'

// Reactive state
const isLoading = ref(false)
const loadingMessage = ref('')
const loadingSubMessage = ref('')
const showError = ref(false)
const errorMessage = ref('')
const queryType = ref('')
const results = ref(null)
const selectedReport = ref(null)
const reportModalOpen = ref(false)

// For the "Search Complete" notification:
const showNotification = ref(false)
const searchTime = ref('0.0')
const resultCount = ref(0)

// Track how many times keys have changed
const keysUpdateCounter = ref(0)

// Store
const reportStore = useReportStore()

// Dev check
const isDev = ref(import.meta.env.DEV)

// On component mount, load any saved reports from localStorage
onMounted(() => {
  reportStore.loadSavedReports()
})

// Called by Header when user updates keys
function handleKeysUpdated() {
  console.log('[MainLayout] keys updated')
  // Increment the counter => triggers watchers in child components
  keysUpdateCounter.value++
}

// Track time for the search
let searchStartTimestamp = 0

// Sub-message cycling
const subMessageInterval = ref(null)
const subMessageIndex = ref(0)
const currentSubMessages = ref([])

function clearSubMessageInterval() {
  if (subMessageInterval.value) {
    clearInterval(subMessageInterval.value)
    subMessageInterval.value = null
  }
  subMessageIndex.value = 0
  currentSubMessages.value = []
}

function startSubMessageCycle(messages) {
  clearSubMessageInterval()
  if (!messages || messages.length === 0) {
    loadingSubMessage.value = ''
    return
  }

  currentSubMessages.value = messages
  loadingSubMessage.value = messages[0]
  subMessageIndex.value = 1

  subMessageInterval.value = setInterval(() => {
    loadingSubMessage.value = messages[subMessageIndex.value]
    subMessageIndex.value = (subMessageIndex.value + 1) % messages.length
  }, 2000)
}

onBeforeUnmount(() => {
  clearSubMessageInterval()
})

// -------------------------------------
// Search events from <SearchSection>
// -------------------------------------
function handleSearchStart(type) {
  console.log('[MainLayout] Received "searchStart" with type:', type)
  
  // Show the spinner
  isLoading.value = true
  results.value = null
  queryType.value = type
  searchStartTimestamp = performance.now()
}

// Watch changes to queryType => update main spinner messages
watch(queryType, (newVal, oldVal) => {
  console.log('[MainLayout] queryType changed from', oldVal, 'to', newVal)
  
  clearSubMessageInterval()

  switch (newVal) {
    case 'routing_query':
      loadingMessage.value = 'Routing Query...'
      loadingSubMessage.value = ''
      break

    case 'sales_leads':
      loadingMessage.value = 'Sales Leads Query...'
      startSubMessageCycle([
        'Searching for companies...',
        'Extracting data...',
        'Getting marketing info...'
      ])
      break

    case 'educational_content':
      loadingMessage.value = 'Research Generation...'
      startSubMessageCycle([
        'Searching for topics...',
        'Creating content plan...',
        'Writing content...'
      ])
      break

    default:
      loadingMessage.value = 'Determining route...'
      loadingSubMessage.value = ''
      break
  }
})

// Search complete => hide spinner, store results, show notification
function handleSearchComplete(searchResults) {
  console.log('[MainLayout] handleSearchComplete =>', searchResults.type)
  queryType.value = searchResults.type
  results.value = searchResults.results

  // Save the final report to localStorage:
  reportStore.saveReport(searchResults.type, searchResults.query, searchResults.results)

  // Turn off spinner
  isLoading.value = false

  // Show a notification
  const elapsed = (performance.now() - searchStartTimestamp) / 1000
  searchTime.value = elapsed.toFixed(1)

  // Count how many results we got
  if (Array.isArray(searchResults.results)) {
    resultCount.value = searchResults.results.length
  } else if (searchResults.results && searchResults.results.results) {
    // e.g. "sales_leads" => results.results array
    resultCount.value = searchResults.results.results.length
  } else {
    resultCount.value = 0
  }

  showNotification.value = true

  // 5-second auto-hide for the toast
  setTimeout(() => {
    showNotification.value = false
  }, 5000)
}

// Search error => hide spinner, display error
function handleSearchError(error) {
  console.error('[MainLayout] Search error:', error)
  isLoading.value = false
  loadingMessage.value = ''
  loadingSubMessage.value = ''
  showError.value = true
  errorMessage.value = error?.message || 'An unexpected error occurred'
}

// Close the error modal
function closeError() {
  showError.value = false
  errorMessage.value = ''
}

// Called by SearchSection if user wants to open settings
function openSettings() {
  console.log('[MainLayout] openSettings clicked')
  // You can directly open the modal in <Header> if needed:
  // headerRef.value.openSettings()
}

// Handle selection of a saved report from Sidebar
function handleSavedReportSelect(savedReport) {
  queryType.value = savedReport.type
  results.value = savedReport.results
  selectedReport.value = null
  reportModalOpen.value = false
}

// Check if we have results to display
const hasResults = computed(() => {
  if (queryType.value === 'sales_leads') {
    return results.value?.results && Array.isArray(results.value.results) && results.value.results.length > 0
  }
  // For research or other content, check if it's an array
  return Array.isArray(results.value) && results.value.length > 0
})
</script>

<style scoped>
/* Basic styling as needed. */
</style>
