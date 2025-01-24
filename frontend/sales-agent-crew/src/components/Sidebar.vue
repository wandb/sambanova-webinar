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
      <!-- Header -->
      <div class="p-4 border-b border-gray-200">
        <h2 
          :class="[
            'font-semibold text-gray-900 whitespace-nowrap flex items-center',
            isCollapsed ? 'justify-center' : ''
          ]"
        >
          <MagnifyingGlassIcon class="w-5 h-5 mr-2" />
          <span :class="{ 'hidden': isCollapsed }">Saved Searches</span>
        </h2>
      </div>

      <!-- Saved Reports List -->
      <div class="overflow-y-auto h-[calc(100%-4rem)]">
        <div 
          v-for="report in reportStore.savedReports" 
          :key="report.id"
          @click="selectReport(report)"
          class="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
          :class="{ 'text-center': isCollapsed }"
        >
          <!-- Collapsed View -->
          <div v-if="isCollapsed" class="flex flex-col items-center">
            <DocumentTextIcon class="w-6 h-6 text-gray-600" />
            <span class="text-xs mt-1">{{ formatTime(report.timestamp) }}</span>
          </div>

          <!-- Expanded View -->
          <div v-else class="space-y-1">
            <div class="font-medium text-gray-900 truncate">
              {{ report.query }}
            </div>
            <div class="flex items-center justify-between text-sm text-gray-500">
              <span class="flex items-center">
                <component 
                  :is="report.type === 'educational_content' ? BookOpenIcon : UserGroupIcon"
                  class="w-4 h-4 mr-1"
                />
                {{ formatType(report.type) }}
              </span>
              <span>{{ formatDate(report.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useReportStore } from '../stores/reportStore'
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'

const reportStore = useReportStore()
const isCollapsed = ref(false)
const emit = defineEmits(['selectReport'])

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
</script>

<style scoped>
/* Ensure the toggle button remains clickable */
button[title='Toggle Sidebar'] {
  z-index: 9999;
}
</style> 