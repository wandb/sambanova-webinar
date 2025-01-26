<template>
  <!-- Outer container uses flex-row so the sidebar, main area, and agent sidebar appear side-by-side -->
  <div class="min-h-screen flex">

    <!-- LEFT SIDEBAR -->
    <Sidebar @selectReport="handleSavedReportSelect" />

    <!-- MAIN COLUMN -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">

      <!-- PAGE HEADER -->
      <Header 
        @keysUpdated="handleKeysUpdated"
        ref="headerRef"
        class="flex-none"
      />

      <!-- MAIN CONTENT WRAPPER -->
      <main class="flex-grow flex flex-col p-4 space-y-4 overflow-y-auto">

        <!-- Pass the currentRunId to <SearchSection> so it uses it in /execute calls -->
        <SearchSection 
          :keysUpdated="keysUpdateCounter"
          :isLoading="isLoading"
          :runId="currentRunId"
          @searchStart="handleSearchStart"
          @searchComplete="handleSearchComplete"
          @searchError="handleSearchError"
          @openSettings="openSettings"
        />

        <SearchNotification
          :show="showNotification"
          :time="searchTime"
          :resultCount="resultCount"
        />

        <!-- LOADING SPINNER -->
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

            <!-- Educational Content Results -->
            <template v-else>
              <ResearchReport :report="results" />
            </template>
          </div>
        </div>

        <!-- FULL REPORT MODAL -->
        <FullReportModal
          v-if="selectedReport"
          :open="reportModalOpen"
          :report-data="selectedReport"
          @close="reportModalOpen = false"
        />
      </main>
    </div>

    <!-- RIGHT SIDEBAR: Real-time Agent Logs for the current user + run ID -->
    <AgentSidebar 
      :userId="clerkUserId" 
      :runId="currentRunId" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onBeforeUnmount } from 'vue'
import { useUser } from '@clerk/vue'
import { v4 as uuidv4 } from 'uuid'

import Header from '@/components/Header.vue'
import SearchSection from '@/components/SearchSection.vue'
import SearchNotification from '@/components/SearchNotification.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import CompanyResultCard from '@/components/CompanyResultCard.vue'
import ResearchReport from '@/components/ResearchReport.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import FullReportModal from '@/components/FullReportModal.vue'
import Sidebar from '@/components/Sidebar.vue'
import AgentSidebar from '@/components/AgentSidebar.vue'

import { useReportStore } from '@/stores/reportStore'

// reactive state
const isLoading = ref(false)
const loadingMessage = ref('')
const loadingSubMessage = ref('')
const showError = ref(false)
const errorMessage = ref('')
const queryType = ref('')
const results = ref(null)
const selectedReport = ref(null)
const reportModalOpen = ref(false)

// "Search Complete" toast
const showNotification = ref(false)
const searchTime = ref('0.0')
const resultCount = ref(0)

// Track how many times keys changed
const keysUpdateCounter = ref(0)

// Our store
const reportStore = useReportStore()

// For dev
const isDev = ref(import.meta.env.DEV)

// Header ref
const headerRef = ref(null)

// Clerk user ID
const { user } = useUser()
const clerkUserId = computed(() => user.value?.id || 'anonymous_user')

// The runId for this search. Must remain consistent for SSE + publish
const currentRunId = ref('')

// On mount, load saved reports
onMounted(() => {
  reportStore.loadSavedReports()
})

// Called by Header
function handleKeysUpdated() {
  keysUpdateCounter.value++
}

let searchStartTimestamp = 0

// sub-message rotation
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

/**
 * Called when SearchSection triggers "searchStart"
 * The first argument is the "detected route type"
 * e.g. "routing_query", "sales_leads", "educational_content"
 */
function handleSearchStart(type) {
  

  // If we are starting a brand-new search, generate a new runId
  // We do this only once per search cycle
  // If "routing_query" then a second "searchStart" with "sales_leads" will happen,
  // so we only set runId if not already set, or always set anew on each brand-new search.
  if (type === 'routing_query' || !currentRunId.value) {
    currentRunId.value = uuidv4()
  }

  // Show spinner
  isLoading.value = true
  results.value = null
  queryType.value = type
  searchStartTimestamp = performance.now()
}

// Watch queryType => update loading messages
watch(queryType, (newVal, oldVal) => {
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

// searchComplete => hide spinner, store results, etc.
function handleSearchComplete(searchResults) {
  queryType.value = searchResults.type
  results.value = searchResults.results

  // Save final report
  reportStore.saveReport(searchResults.type, searchResults.query, searchResults.results)

  // Turn off spinner
  isLoading.value = false

  // Show notification
  const elapsed = (performance.now() - searchStartTimestamp) / 1000
  searchTime.value = elapsed.toFixed(1)

  if (Array.isArray(searchResults.results)) {
    resultCount.value = searchResults.results.length
  } else if (searchResults.results?.results && Array.isArray(searchResults.results.results)) {
    resultCount.value = searchResults.results.results.length
  } else {
    resultCount.value = 0
  }

  showNotification.value = true

  setTimeout(() => {
    showNotification.value = false
  }, 5000)
}

// searchError => hide spinner, show error
function handleSearchError(error) {
  console.error('[MainLayout] Search error:', error)
  isLoading.value = false
  loadingMessage.value = ''
  loadingSubMessage.value = ''
  showError.value = true
  errorMessage.value = error?.message || 'An unexpected error occurred'
}

// close error modal
function closeError() {
  showError.value = false
  errorMessage.value = ''
}

// open settings
function openSettings() {
  headerRef.value.openSettings()
}

// handle sidebar saved report
function handleSavedReportSelect(savedReport) {
  queryType.value = savedReport.type
  results.value = savedReport.results
  selectedReport.value = null
  reportModalOpen.value = false
}

// computed => do we have results to display?
const hasResults = computed(() => {
  if (queryType.value === 'sales_leads') {
    return results.value?.results && Array.isArray(results.value.results) && results.value.results.length > 0
  }
  return Array.isArray(results.value) && results.value.length > 0
})
</script>

<style scoped>
/* Basic styling as needed. */
</style>
