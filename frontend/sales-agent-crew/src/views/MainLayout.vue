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

        <!-- SearchSection: triggers search events -->
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

            <!-- Research Report Results -->
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
import { ref, onMounted, computed } from 'vue'
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

// Store
const reportStore = useReportStore()

// Add isDev ref
const isDev = ref(import.meta.env.DEV)

// On component mount, load any saved reports from localStorage
onMounted(() => {
  reportStore.loadSavedReports()
})

// Access saved reports if needed
const savedReports = computed(() => reportStore.savedReports)

// Called by Header when user updates keys
function handleKeysUpdated() {
  console.log('[MainLayout] keys updated')
}

// -------------------------------------
// Search events from <SearchSection>
// -------------------------------------
let searchStartTimestamp = 0

// Search start => show spinner
function handleSearchStart(type) {
  console.log('[MainLayout] Search started with type:', type)
  queryType.value = type
  isLoading.value = true
  results.value = null
  searchStartTimestamp = performance.now()

  if (type === 'sales_leads') {
    loadingMessage.value = 'Searching for leads...'
    loadingSubMessage.value = 'This may take a moment'
  } else if (type === 'educational_content') {
    loadingMessage.value = 'Generating educational material...'
    loadingSubMessage.value = 'Researching and compiling info...'
  } else {
    loadingMessage.value = 'Determining route...'
    loadingSubMessage.value = ''
  }
}

// Search complete => hide spinner, store results, show notification
function handleSearchComplete(searchResults) {
  queryType.value = searchResults.type
  results.value = searchResults.results
  isLoading.value = false
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

// For opening full report from the ResearchReport child
function onShowFullReport(reportData) {
  selectedReport.value = reportData
  reportModalOpen.value = true
}

// Called by SearchSection if user wants to open settings
function openSettings() {
  console.log('[MainLayout] openSettings clicked')
  // If you want to actually open the modal in Header:
  // headerRef.value.openSettings()
}

// Handle selection of a saved report from Sidebar
function handleSavedReportSelect(savedReport) {
  queryType.value = savedReport.type
  results.value = savedReport.results
  selectedReport.value = null
  reportModalOpen.value = false
}

// Update computed property to handle both formats
const hasResults = computed(() => {
  if (queryType.value === 'sales_leads') {
    return results.value?.results && Array.isArray(results.value.results) && results.value.results.length > 0
  }
  // For research reports, check direct array
  return Array.isArray(results.value) && results.value.length > 0
})
</script>

<style scoped>
/* You can adjust background colors for the sidebar vs main area or add more styling as needed. */
</style>
