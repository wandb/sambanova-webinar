<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <!-- Report Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{ report.title }}</h1>
      <div class="mt-2 text-gray-600">
        <p class="font-medium">High Level Goal:</p>
        <p>{{ report.high_level_goal }}</p>
      </div>
    </div>

    <!-- Report Sections -->
    <div class="space-y-4">
      <div v-for="(section, index) in report.content_outline" :key="index"
           class="border border-gray-200 rounded-lg">
        <button @click="toggleSection(index)"
                class="w-full px-4 py-3 flex justify-between items-center hover:bg-gray-50">
          <span class="font-medium text-gray-900">{{ section }}</span>
          <svg class="w-5 h-5 transform transition-transform"
               :class="{ 'rotate-180': expandedSections[index] }"
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <div v-show="expandedSections[index]"
             class="px-4 py-3 border-t border-gray-200">
          <div class="prose max-w-none" v-html="formatContent(section)"></div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 flex justify-end space-x-4">
      <button @click="downloadPDF"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        Download PDF
      </button>
      <button @click="showFullReport"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
        View Full Report
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { jsPDF } from 'jspdf'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

const expandedSections = ref({})

// Initialize all sections as collapsed
onMounted(() => {
  props.report.content_outline.forEach((_, index) => {
    expandedSections.value[index] = false
  })
})

const toggleSection = (index) => {
  expandedSections.value[index] = !expandedSections.value[index]
}

// Format content with markdown/HTML
const formatContent = (content) => {
  // Add markdown/HTML formatting logic here
  return content
}

const downloadPDF = () => {
  const doc = new jsPDF()
  // Add PDF generation logic here
}

const showFullReport = () => {
  // Emit event to show full report modal/sidebar
  emit('showFullReport', props.report)
}
</script> 