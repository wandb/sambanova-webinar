<template>
  <!-- Outer container uses flex-row so the sidebar and main area appear side-by-side -->
  <div class="min-h-screen flex">
    
    <!-- 1) SIDEBAR -->
    <Sidebar
      @selectReport="handleSavedReportSelect"
    />

    <!-- 2) MAIN COLUMN -->
    <div class="flex-1 flex flex-col">

      <!-- PAGE HEADER -->
      <Header 
        @keysUpdated="handleKeysUpdated"
        ref="headerRef"
      />

      <!-- MAIN CONTENT WRAPPER -->
      <main class="flex-grow flex flex-col p-4 space-y-4">

        <!-- SearchSection: triggers search events -->
        <SearchSection 
          @searchStart="handleSearchStart"
          @searchComplete="handleSearchComplete"
          @searchError="handleSearchError"
          @openSettings="openSettings"
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
          :error-message="errorMessage"
          @close="closeError"
        />

        <!-- RESULTS SECTION -->
        <div v-if="!isLoading && results">
          <!-- If these are sales leads, show CompanyResultCard -->
          <div v-if="queryType === 'sales_leads'">
            <div class="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
              <CompanyResultCard
                v-for="(company, index) in results"
                :key="index"
                :company="company"
              />
            </div>
          </div>

          <!-- If it's educational content, show a ResearchReport -->
          <div v-else-if="queryType === 'educational_content'">
            <div class="space-y-4">
              <ResearchReport
                :report="results"
                @showFullReport="onShowFullReport"
              />
            </div>
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

// Inside script setup:
const reportStore = useReportStore()

// Load saved reports when component mounts
onMounted(() => {
  reportStore.loadSavedReports()
})

// Access saved reports
const savedReports = computed(() => reportStore.savedReports)

// Called by Header when user updates keys
function handleKeysUpdated() {
  console.log('[MainLayout] keys updated')
}

// Search start => show spinner
function handleSearchStart(type) {
  console.log('[MainLayout] searchStart => type:', type)
  isLoading.value = true
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

// Search complete => hide spinner, store results
function handleSearchComplete({ type, query, results: newResults }) {
  console.log('[MainLayout] searchComplete => type:', type, 'results:', newResults)
  isLoading.value = false
  loadingMessage.value = ''
  loadingSubMessage.value = ''
  queryType.value = type
  results.value = newResults

  // Save the report if we got valid results
  if (newResults && (type === 'educational_content' || type === 'sales_leads')) {
    reportStore.saveReport(type, query, newResults)
  }
}

// Search error => hide spinner, display error
function handleSearchError(error) {
  console.error('[MainLayout] searchError =>', error)
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
  // Access the header's openSettings method, which calls the SettingsModal
  console.log('[MainLayout] openSettings clicked')
  // If you want to actually open it:
  // this.$refs.headerRef.openSettings()   <-- if using Options API
  // or headerRef.value.openSettings() if using <script setup> with a template ref
}

// Add this function to handle saved report selection
function handleSavedReportSelect({ type, query, results }) {
  queryType.value = type
  results.value = results
  // You might want to update other state as needed
}
</script>

<style scoped>
/* You can adjust background colors for the sidebar vs main area or add more styling as needed. */
</style>
