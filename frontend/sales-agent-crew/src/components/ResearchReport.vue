<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <!-- Iterate through chapters -->
    <div 
      v-for="(chapter, index) in report" 
      :key="index" 
      class="mb-6 border-b last:border-b-0 pb-6 last:pb-0"
    >
      <!-- Chapter Header -->
      <button
        @click="toggleChapter(index)"
        class="w-full text-left flex justify-between items-center py-3 px-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div class="flex items-center space-x-3">
          <BookOpenIcon class="w-5 h-5 text-primary-600" />
          <h2 class="font-semibold text-gray-900">{{ chapter.title }}</h2>
        </div>
        <ChevronDownIcon
          class="w-5 h-5 text-gray-500 transform transition-transform duration-200"
          :class="{ 'rotate-180': expandedChapters[index] }"
        />
      </button>

      <!-- Chapter Content -->
      <div
        v-show="expandedChapters[index]"
        class="mt-4 px-4 space-y-4"
      >
        <!-- High Level Goal -->
        <div class="flex items-start space-x-3 bg-blue-50 p-3 rounded-lg">
          <FlagIcon class="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 class="font-medium text-blue-900">High Level Goal</h4>
            <p class="text-blue-800">{{ chapter.high_level_goal }}</p>
          </div>
        </div>

        <!-- Why Important -->
        <div class="flex items-start space-x-3 bg-amber-50 p-3 rounded-lg">
          <LightBulbIcon class="w-5 h-5 text-amber-600 mt-0.5" />
          <div>
            <h4 class="font-medium text-amber-900">Why Important</h4>
            <p class="text-amber-800">{{ chapter.why_important }}</p>
          </div>
        </div>

        <!-- Generated Content -->
        <div class="prose max-w-none mt-6 text-gray-700"
             v-html="formatMarkdown(chapter.generated_content)">
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end space-x-4 mt-6">
      <button
        @click="showFullReport"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <DocumentTextIcon class="w-5 h-5 mr-2" />
        View Full Report
      </button>
      <button
        @click="downloadPDF"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <ArrowDownTrayIcon class="w-5 h-5 mr-2" />
        Download PDF
      </button>
    </div>

    <!-- Full Report Modal -->
    <FullReportModal
      :open="isFullReportOpen"
      :reportData="report"
      @close="isFullReportOpen = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { jsPDF } from 'jspdf'
import {
  ArrowDownTrayIcon,
  ChevronDownIcon,
  DocumentMagnifyingGlassIcon,
  BookOpenIcon,
  FlagIcon,
  LightBulbIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'
import FullReportModal from './FullReportModal.vue'

const props = defineProps({
  report: {
    type: Array,
    required: true
  }
})

// Track which chapters are expanded
const expandedChapters = ref({})

// Format the report data for the modal
const formattedReport = computed(() => {
  return props.report.map(chapter => ({
    title: chapter.title,
    content: chapter.generated_content,
    sources: chapter.sources || [],
    metadata: {
      high_level_goal: chapter.high_level_goal,
      why_important: chapter.why_important
    }
  }))
})

// Toggle a given chapter by index
function toggleChapter(index) {
  expandedChapters.value[index] = !expandedChapters.value[index]
}

// Convert markdown => safe HTML
function formatMarkdown(text = '') {
  const rawHtml = marked(text)
  return DOMPurify.sanitize(rawHtml)
}

// Basic PDF generator
function downloadPDF() {
  const doc = new jsPDF()
  let yOffset = 20

  props.report.forEach((chapter, index) => {
    if (index > 0) {
      doc.addPage()
      yOffset = 20
    }
    // Title
    doc.setFontSize(16)
    doc.text(chapter.title, 20, yOffset)
    yOffset += 10

    doc.setFontSize(12)
    // High Level Goal
    doc.text(`High Level Goal: ${chapter.high_level_goal || ''}`, 20, yOffset)
    yOffset += 10

    // Why Important
    doc.text(`Why Important: ${chapter.why_important || ''}`, 20, yOffset)
    yOffset += 10

    // Content
    const lines = doc.splitTextToSize(chapter.generated_content || '', 170)
    doc.text(lines, 20, yOffset + 5)
    yOffset += (lines.length * 7) + 15
  })

  doc.save('research_report.pdf')
}

const isFullReportOpen = ref(false)

const showFullReport = () => {
  isFullReportOpen.value = true
}

// Initialize with first chapter expanded
onMounted(() => {
  if (props.report?.length > 0) {
    expandedChapters.value[0] = true
  }
})
</script>

<style scoped>
.prose {
  @apply text-gray-700;
}
.prose p {
  @apply mb-4;
}
.prose ul {
  @apply list-disc list-inside mb-4;
}
.prose h3 {
  @apply text-lg font-semibold mb-2;
}
</style> 