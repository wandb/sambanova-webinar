<template>
  <TransitionRoot appear :show="open" as="template">
    <Dialog as="div" @close="$emit('close')" class="relative z-50">
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
              <DialogTitle as="h3" class="text-2xl font-bold text-gray-900 mb-4">
                {{ reportData.title }}
              </DialogTitle>

              <div class="mt-4 space-y-6 max-h-[70vh] overflow-y-auto">
                <!-- Iterate through all sections -->
                <div v-for="(section, index) in reportData" :key="index" class="mb-8">
                  <h2 class="text-xl font-bold text-gray-900 mb-4">{{ section.title }}</h2>
                  
                  <!-- High Level Goal -->
                  <div class="mb-4">
                    <h3 class="font-semibold text-gray-800">High Level Goal</h3>
                    <p class="text-gray-600">{{ section.high_level_goal }}</p>
                  </div>

                  <!-- Why Important -->
                  <div class="mb-4">
                    <h3 class="font-semibold text-gray-800">Why Important</h3>
                    <p class="text-gray-600">{{ section.why_important }}</p>
                  </div>

                  <!-- Content -->
                  <div class="mb-4">
                    <h3 class="font-semibold text-gray-800">Content</h3>
                    <div class="prose prose-sm max-w-none" v-html="formatMarkdown(section.generated_content)"></div>
                  </div>

                  <!-- Sources -->
                  <div class="mb-4">
                    <h3 class="font-semibold text-gray-800">Sources</h3>
                    <ul class="list-disc pl-5">
                      <li v-for="(source, sourceIndex) in section.sources" 
                          :key="sourceIndex"
                          class="text-blue-600 hover:underline">
                        <a :href="source" target="_blank">{{ source }}</a>
                      </li>
                    </ul>
                  </div>

                  <!-- Section divider -->
                  <div v-if="index < reportData.length - 1" class="border-t border-gray-200 my-6"></div>
                </div>
              </div>

              <!-- Close button -->
              <div class="mt-6 flex justify-end">
                <button
                  @click="$emit('close')"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <XMarkIcon class="w-5 h-5 mr-2" />
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
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { XMarkIcon, DocumentTextIcon, LinkIcon, LightBulbIcon, AdjustmentsHorizontalIcon as TargetIcon } from '@heroicons/vue/24/outline'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

defineProps({
  open: Boolean,
  reportData: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

const formatMarkdown = (content) => {
  if (!content) return ''
  const rawHtml = marked(content)
  return DOMPurify.sanitize(rawHtml)
}
</script>

<style scoped>
:deep(.prose) {
  @apply text-gray-600;
}

:deep(.prose h1), :deep(.prose h2), :deep(.prose h3) {
  @apply text-gray-900 font-semibold mt-4 mb-2;
}

:deep(.prose p) {
  @apply mb-4;
}

:deep(.prose ul) {
  @apply list-disc list-inside mb-4;
}

:deep(.prose a) {
  @apply text-blue-600 hover:underline;
}
</style> 