<template>
    <div class="deep-research max-w-4xl mx-auto">
  
      <!-- Add debug info -->
      <div v-if="!finalReport" class="text-gray-500 p-4 bg-gray-50 rounded-lg">
        <p class="text-center">No research data available</p>
      </div>
  
      <template v-else>
        <!-- Main content with improved styling -->
        <div class="report-content prose prose-lg dark:prose-invert max-w-none">
          <div v-html="renderMarkdown(finalReport)" class="space-y-4"></div>
        </div>
  
        <!-- Enhanced Citations Section -->
        <div
          v-if="parsedCitations.length > 0"
          class="citations mt-12 bg-gray-50 dark:bg-neutral-900 rounded-xl p-6"
        >
          <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
            Sources & Citations
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="citation in parsedCitations"
              :key="citation.id"
              class="citation-card bg-white dark:bg-neutral-800 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-200"
            >
              <div class="flex items-start space-x-4">
                <!-- Website Icon -->
                <div class="flex-shrink-0 w-6 h-6">
                  <img 
                    :src="`https://www.google.com/s2/favicons?domain=${new URL(citation.url).hostname}&sz=64`"
                    :alt="citation.title"
                    class="w-full h-full object-contain"
                  />
                </div>
                
                <!-- Citation Content -->
                <div class="flex-1 min-w-0">
                  <h3 class="font-medium text-gray-900 dark:text-white truncate">
                    {{ citation.title }}
                  </h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                    {{ citation.description }}
                  </p>
                  <a
                    :href="citation.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center mt-2 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    Visit source
                    <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
  
    </div>
  </template>
  
  <script setup>
  import { defineProps, computed } from 'vue'
  import { marked } from 'marked'
  
  const props = defineProps({
    parsed: {
      type: Object,
      required: true
    }
  })
  
  // Configure marked options for better markdown rendering
  marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Convert line breaks to <br>
    headerIds: true, // Add IDs to headers
    mangle: false, // Don't escape HTML
    smartLists: true, // Use smarter list behavior
  })
  
  const renderer = new marked.Renderer()
  
  // Improve table rendering
  renderer.table = (header, body) => {
    return `
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700 my-4">
        <thead class="bg-gray-50 dark:bg-gray-800">
          ${header}
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          ${body}
        </tbody>
      </table>
    `
  }
  
  // Improve cell rendering
  renderer.tablecell = (content, flags) => {
    const tag = flags.header ? 'th' : 'td'
    const classes = flags.header 
      ? 'px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider'
      : 'px-6 py-4 whitespace-normal text-sm text-gray-900 dark:text-gray-100'
    return `<${tag} class="${classes}">${content}</${tag}>`
  }
  
  marked.setOptions({ renderer })
  
  const finalReport = computed(() => {
    if (!props.parsed?.data?.final_report) return ''
    
    // Process the content to handle objects
    let content = props.parsed.data.final_report
    
    // Replace [object Object] with proper formatting
    content = content.replace(/\[object Object\]/g, '')
    
    // Clean up multiple newlines
    content = content.replace(/\n{3,}/g, '\n\n')
    
    // Ensure tables are properly formatted
    content = content.replace(/(\|[^\n]+\|)\n(?!\|)/g, '$1\n\n')
    
    return content
  })
  
  const parsedCitations = computed(() => {
    if (!props.parsed?.data?.citations) return []
    return props.parsed.data.citations.map((citation, index) => {
      try {
        const url = new URL(citation.url)
        return {
          ...citation,
          id: index,
          title: citation.title || url.hostname,
          description: citation.description || 'No description available'
        }
      } catch (e) {
        return {
          ...citation,
          id: index,
          title: citation.title || 'Unknown Source',
          description: citation.description || 'No description available'
        }
      }
    })
  })
  
  const renderMarkdown = (text) => {
    return marked(text || '')
  }
  
  </script>
  
  <style scoped>
  .report-content :deep(h1) {
    @apply text-2xl font-bold mb-4 mt-6;
  }
  
  .report-content :deep(h2) {
    @apply text-xl font-bold mb-3 mt-5;
  }
  
  .report-content :deep(h3) {
    @apply text-lg font-bold mb-2 mt-4;
  }
  
  .report-content :deep(p) {
    @apply text-base mb-3 leading-relaxed text-gray-800 dark:text-gray-200;
  }
  
  .report-content :deep(ul), 
  .report-content :deep(ol) {
    @apply mb-3 pl-5 space-y-1.5 text-base;
  }
  
  .report-content :deep(li) {
    @apply leading-relaxed text-base;
  }
  
  .report-content :deep(a) {
    @apply text-blue-600 hover:text-blue-800 underline;
  }
  
  .report-content :deep(blockquote) {
    @apply pl-4 border-l-4 border-gray-300 italic my-4 text-base;
  }
  
  .report-content :deep(code) {
    @apply bg-gray-100 dark:bg-gray-800 rounded px-1 py-0.5 text-sm;
  }
  
  .report-content :deep(pre) {
    @apply bg-gray-100 dark:bg-gray-800 rounded p-4 overflow-x-auto my-4;
  }
  
  .report-content :deep(table) {
    @apply w-full border-collapse my-4;
  }
  
  .report-content :deep(th),
  .report-content :deep(td) {
    @apply border border-gray-300 dark:border-gray-700 px-3 py-2 text-left text-sm;
  }
  
  .report-content :deep(th) {
    @apply bg-gray-100 dark:bg-gray-800 font-semibold;
  }
  
  .report-content :deep(tr:nth-child(even)) {
    @apply bg-gray-50 dark:bg-gray-900;
  }
  
  /* Update citation card text sizes */
  .citation-card h3 {
    @apply text-base;
  }
  
  .citation-card p {
    @apply text-sm;
  }
  </style>
  