<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <!-- Header -->
              <DialogTitle as="h3" class="text-2xl font-bold leading-6 text-gray-900 mb-4">
                {{ report.title }}
              </DialogTitle>

              <!-- Content -->
              <div class="mt-4 space-y-6 max-h-[70vh] overflow-y-auto">
                <!-- High Level Goal -->
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">High Level Goal</h4>
                  <p class="mt-2 text-gray-600">{{ report.high_level_goal }}</p>
                </div>

                <!-- Why Important -->
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Why This Matters</h4>
                  <p class="mt-2 text-gray-600">{{ report.why_important }}</p>
                </div>

                <!-- Sources -->
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Sources</h4>
                  <ul class="mt-2 space-y-1">
                    <li v-for="(source, index) in report.sources" :key="index">
                      <a :href="source" target="_blank" class="text-primary-600 hover:text-primary-700">
                        {{ source }}
                      </a>
                    </li>
                  </ul>
                </div>

                <!-- Content -->
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">Content</h4>
                  <div class="mt-2 prose max-w-none" v-html="formattedContent"></div>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-6 flex justify-end space-x-4">
                <button
                  @click="downloadPDF"
                  class="inline-flex justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                >
                  Download PDF
                </button>
                <button
                  @click="closeModal"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'

const props = defineProps({
  isOpen: Boolean,
  report: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const closeModal = () => {
  emit('close')
}

const formattedContent = computed(() => {
  // Add markdown/HTML formatting logic here
  return props.report.generated_content
})

const downloadPDF = () => {
  const doc = new jsPDF()
  
  // Add custom font
  doc.setFont('helvetica', 'normal')
  
  // Title
  doc.setFontSize(24)
  doc.text(props.report.title, 20, 20)
  
  // High Level Goal
  doc.setFontSize(16)
  doc.text('High Level Goal', 20, 40)
  doc.setFontSize(12)
  doc.text(props.report.high_level_goal, 20, 50)
  
  // Why Important
  doc.setFontSize(16)
  doc.text('Why This Matters', 20, 70)
  doc.setFontSize(12)
  doc.text(props.report.why_important, 20, 80)
  
  // Sources
  doc.setFontSize(16)
  doc.text('Sources', 20, 100)
  doc.setFontSize(12)
  props.report.sources.forEach((source, index) => {
    doc.text(source, 20, 110 + (index * 10))
  })
  
  // Content
  doc.setFontSize(16)
  doc.text('Content', 20, 140)
  doc.setFontSize(12)
  doc.text(props.report.generated_content, 20, 150)
  
  // Download
  doc.save(`${props.report.title.toLowerCase().replace(/\s+/g, '_')}.pdf`)
}
</script> 