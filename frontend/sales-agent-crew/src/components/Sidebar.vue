<template>
  <div class="relative h-full">
    <!-- Toggle collapse button -->
    <button
      @click="isCollapsed = !isCollapsed"
      class="absolute -right-3 top-4 z-20 p-1.5 bg-white rounded-full shadow-md hover:bg-gray-50 transition"
      :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
    >
      <ChevronLeftIcon
        :class="[
          'h-4 w-4 text-gray-600 transition-transform duration-300',
          isCollapsed ? 'rotate-180' : ''
        ]"
      />
    </button>

    <!-- Sidebar Container -->
    <div
      :class="[
        'h-full bg-white shadow-lg transition-all duration-300 overflow-hidden',
        isCollapsed ? 'w-16' : 'w-64'
      ]"
    >
      <!-- Header with Filter and Bulk Actions -->
      <div class="p-4 border-b border-gray-200 space-y-3">
        <div 
          :class="[
            'flex items-center justify-between',
            isCollapsed ? 'flex-col space-y-2' : ''
          ]"
        >
          <h2 
            :class="[
              'font-semibold text-gray-900 whitespace-nowrap flex items-center',
              isCollapsed ? 'justify-center' : ''
            ]"
          >
            <MagnifyingGlassIcon class="w-5 h-5 mr-2" />
            <span :class="{ 'hidden': isCollapsed }">Saved Searches</span>
          </h2>

          <!-- Filter Dropdown -->
          <div v-if="!isCollapsed" class="flex items-center space-x-2">
            <label for="filterType" class="text-sm text-gray-600">Filter:</label>
            <select
              id="filterType"
              v-model="filterType"
              class="border border-gray-300 rounded-md p-1 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="all">All</option>
              <option value="educational_content">Research</option>
              <option value="sales_leads">Sales Leads</option>
            </select>
          </div>
        </div>

        <!-- Bulk Action Buttons -->
        <div v-if="!isCollapsed" class="flex items-center justify-between">
          <button
            @click="exportAllReports"
            class="flex items-center space-x-1 text-sm text-gray-700 hover:underline focus:outline-none"
          >
            <ArchiveBoxArrowDownIcon class="w-4 h-4" />
            <span>Export All (JSON)</span>
          </button>
          <button
            @click="clearAllConfirm"
            class="flex items-center space-x-1 text-sm text-red-600 hover:underline focus:outline-none"
          >
            <TrashIcon class="w-4 h-4" />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      <!-- Saved Reports List -->
      <div 
        class="overflow-y-auto max-h-[calc(100vh-8rem)]"
      >
        <div 
          v-for="report in filteredReports" 
          :key="report.id"
          class="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors group"
        >
          <!-- Entire row clickable except the buttons -->
          <div
            class="flex items-start justify-between w-full"
            @click="selectReport(report)"
          >
            <!-- Collapsed View -->
            <div v-if="isCollapsed" class="flex flex-col items-center w-full">
              <component 
                :is="report.type === 'educational_content' ? BookOpenIcon : UserGroupIcon"
                class="w-6 h-6 text-gray-600 mb-1"
              />
              <span class="text-xs text-gray-500">
                {{ formatDate(report.timestamp) }}
              </span>
              <span class="text-xs text-gray-500">
                {{ formatTime(report.timestamp) }}
              </span>
            </div>

            <!-- Expanded View -->
            <div v-else class="space-y-1 w-full pr-2">
              <div 
                class="font-medium break-words"
                :class="reportTextColor(report.type)"
              >
                {{ capitalizeFirstLetter(report.query) }}
              </div>
              <div class="flex items-center justify-between text-sm text-gray-500">
                <span class="flex items-center space-x-1">
                  <component 
                    :is="report.type === 'educational_content' ? BookOpenIcon : UserGroupIcon"
                    class="w-4 h-4"
                  />
                  <span>{{ formatType(report.type) }}</span>
                </span>
                <span>
                  {{ formatDate(report.timestamp) }} 
                  <span class="ml-1">| {{ formatTime(report.timestamp) }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- Individual Action Buttons (only in expanded mode) -->
          <div 
            v-if="!isCollapsed" 
            class="flex items-center justify-end mt-2 space-x-4 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <!-- Export Single -->
            <button
              @click.stop="exportReport(report)"
              class="flex items-center space-x-1 text-sm text-gray-600 hover:underline focus:outline-none"
              title="Export to JSON"
            >
              <ArchiveBoxArrowDownIcon class="w-4 h-4" />
              <span>Export</span>
            </button>
            <!-- Delete Single -->
            <button
              @click.stop="deleteReport(report)"
              class="flex items-center space-x-1 text-sm text-red-600 hover:underline focus:outline-none"
              title="Delete This Report"
            >
              <TrashIcon class="w-4 h-4" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useReportStore } from '../stores/reportStore'
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  UserGroupIcon,
  ArchiveBoxArrowDownIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const reportStore = useReportStore()
const isCollapsed = ref(false)
const filterType = ref('all')
const emit = defineEmits(['selectReport'])

/**
 * Existing methods and references
 */
function selectReport(report) {
  emit('selectReport', {
    type: report.type,
    query: report.query,
    results: report.results
  })
}

function formatType(type) {
  return type === 'educational_content' ? 'Research' : 'Sales Leads'
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleDateString()
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

/**
 * New functionalities below
 */

// Capitalize the first letter of the query text
function capitalizeFirstLetter(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// Color code based on type: green for research, blue for sales leads
function reportTextColor(type) {
  return type === 'educational_content' ? 'text-green-600' : 'text-blue-600'
}

// Computed filtered reports
const filteredReports = computed(() => {
  if (filterType.value === 'all') {
    return reportStore.savedReports
  } else {
    return reportStore.savedReports.filter(r => r.type === filterType.value)
  }
})

// Export to JSON for a single report
function exportReport(report) {
  try {
    const fileName = `${report.query.replace(/\s+/g, '_')}.json`
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(report, null, 2))
    const dlAnchorElem = document.createElement('a')
    dlAnchorElem.setAttribute('href', dataStr)
    dlAnchorElem.setAttribute('download', fileName)
    dlAnchorElem.click()
  } catch (error) {
    console.error('Error exporting report:', error)
  }
}

// Export all reports to JSON
function exportAllReports() {
  try {
    const allReports = reportStore.savedReports
    const fileName = 'all_saved_reports.json'
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(allReports, null, 2))
    const dlAnchorElem = document.createElement('a')
    dlAnchorElem.setAttribute('href', dataStr)
    dlAnchorElem.setAttribute('download', fileName)
    dlAnchorElem.click()
  } catch (error) {
    console.error('Error exporting all reports:', error)
  }
}

// Delete a single report
function deleteReport(report) {
  if (confirm(`Are you sure you want to delete this report?`)) {
    reportStore.deleteReport(report.id) // Assume store has a deleteReport action/mutation
  }
}

// Clear all reports
function clearAllConfirm() {
  if (confirm(`Are you sure you want to clear all saved reports? This cannot be undone.`)) {
    reportStore.clearAllReports() // Assume store has a clearAllReports action/mutation
  }
}
</script>

<style scoped>
/* Ensure the toggle button remains clickable */
button[title='Expand Sidebar'],
button[title='Collapse Sidebar'] {
  z-index: 9999;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background-color: #cccccc;
  border-radius: 9999px;
}
</style>
