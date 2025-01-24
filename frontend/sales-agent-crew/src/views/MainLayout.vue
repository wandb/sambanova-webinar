<template>
  <!-- Outer container uses flex-row so the sidebar and main area appear side-by-side -->
  <div class="min-h-screen flex flex-row">
    
    <!-- 1) SIDEBAR -->
    <aside
      class="w-64 bg-gray-50 border-r border-gray-200 p-6 hidden md:block"
    >
      <!-- Replace with your actual sidebar content or component -->
      <h2 class="text-xl font-bold mb-4">My Sidebar</h2>
      <nav class="space-y-2">
        <a href="#" class="block py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md px-2">
          Dashboard
        </a>
        <a href="#" class="block py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md px-2">
          Leads
        </a>
        <a href="#" class="block py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md px-2">
          Reports
        </a>
      </nav>
    </aside>

    <!-- 2) MAIN COLUMN -->
    <div class="flex flex-col w-full">

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
import { ref } from 'vue'
import Header from '@/components/Header.vue'
import SearchSection from '@/components/SearchSection.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import CompanyResultCard from '@/components/CompanyResultCard.vue'
import ResearchReport from '@/components/ResearchReport.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import FullReportModal from '@/components/FullReportModal.vue'

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
function handleSearchComplete({ type, results: newResults }) {
  console.log('[MainLayout] searchComplete => type:', type, 'results:', newResults)
  isLoading.value = false
  loadingMessage.value = ''
  loadingSubMessage.value = ''
  queryType.value = type
  results.value = newResults
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
</script>

<style scoped>
/* You can adjust background colors for the sidebar vs main area or add more styling as needed. */
</style>
