<template>
    <div class="deep-research max-w-4xl mx-auto px-4 py-4">
      <!-- If there's no finalReport, show a placeholder message -->
      <div v-if="!finalReport">
        <p class="text-center text-gray-500 italic">No research data available.</p>
      </div>
      <template v-else>
        <!-- Main Markdown-Rendered Content -->
        <div class="report-content prose prose-lg dark:prose-invert max-w-none mb-8">
          <div v-html="renderMarkdown(finalReport)"></div>
        </div>
  
        <!-- Citations Section (only if we actually have a citations block) -->
        <div v-if="citationsBlockFound" class="mt-6">
          <!-- If we have no bullet lines (citations), show a small note -->
          <div v-if="citations.length === 0" class="text-sm text-red-500">
            Citations block found, but no bullet lines matched. Check your bullet format!
          </div>
        </div>
  
        <!-- If citations exist, show them in a card layout with pagination + search -->
        <div v-if="citations.length > 0" class="citations-container space-y-4">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
            Sources & Citations ({{ totalCitationsCount }})
          </h2>
  
          <!-- Optional Search Input -->
          <div class="flex gap-2 items-center mb-2">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search citations..."
              class="flex-1 px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
  
          <!-- Citation Cards + Pagination Controls -->
          <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <!-- Cards Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="(cit, idx) in pagedCitations"
                :key="cit.id"
                class="citation-card flex flex-col bg-white dark:bg-gray-800 p-4 rounded-md shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow"
              >
                <div class="flex items-start gap-2 mb-2">
                  <img
                    :src="getFavicon(cit.url)"
                    class="w-6 h-6 object-cover rounded"
                    alt="favicon"
                  />
                  <h3 class="font-semibold text-sm leading-snug text-gray-800 dark:text-gray-100 flex-1">
                    {{ cit.title }}
                  </h3>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-300 flex-1 mb-2 line-clamp-3">
                  <!-- If there's a snippet, place it here. We only have title & url now. -->
                </p>
                <!-- Citation Link -->
                <div class="mt-auto pt-2">
                  <a
                    v-if="cit.url"
                    :href="cit.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline text-xs break-all"
                  >
                    {{ getDomain(cit.url) }}
                    <svg
                      class="w-3 h-3 ml-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4m4-4V6m0 0h-4m4 0l-8 8"
                      />
                    </svg>
                  </a>
                  <span v-else class="text-sm text-gray-400 dark:text-gray-500">
                    No URL provided
                  </span>
                </div>
              </div>
            </div>
  
            <!-- Pagination Controls -->
            <div class="mt-4 flex items-center justify-center gap-2">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                Prev
              </button>
              <span class="text-sm">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </template>
  
  <script setup>
  import { defineProps, computed, ref, onMounted } from 'vue'
  import { marked } from 'marked'
  
  // ---- PROPS ----
  const props = defineProps({
    parsed: {
      type: Object,
      default: () => ({})
    }
  })
  
  // ---- MARKED SETUP ----
  const renderer = new marked.Renderer()
  // open links in new tab
  renderer.link = function (href, title, text) {
    return `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`
  }
  marked.setOptions({
    renderer,
    gfm: true,
    breaks: false,
    mangle: false
  })
  function renderMarkdown(text) {
    return marked(text || '')
  }
  
  // ---- GET final_report ----
  const finalReport = computed(() => {
    // If your JSON is in a different shape, adjust here:
    const raw = props.parsed?.data?.final_report
    if (!raw) return ''
  
    // Remove the Citations section from the main body
    const headingRegex = /(^|\n)##\s*Citations\s*(\n|$)/i
    const idx = raw.search(headingRegex)
    if (idx === -1) {
      // no "## Citations" found, so just return entire text
      return raw
    }
    // Return everything up to the "## Citations" heading
    return raw.slice(0, idx).trim()
  })
  
  // ---- CITATIONS PARSER ----
  // We'll see if we even find "## Citations" in the text:
  const citationsBlockFound = ref(false)
  
  const citations = computed(() => {
    const text = props.parsed?.data?.final_report
    if (!text) {
      console.log('[DeepResearch] No final_report text, citations = []')
      return []
    }
  
    // Find "## Citations"
    const headingRegex = /(^|\n)##\s*Citations\s*(\n|$)/i
    const startIndex = text.search(headingRegex)
    if (startIndex === -1) {
      console.log('[DeepResearch] "## Citations" not found at all.')
      return []
    }
  
    // Mark the block as found (for debugging in template)
    citationsBlockFound.value = true
  
    // slice from "## Citations" to end OR next heading
    let citationsBlock = text.slice(startIndex)
    // find next heading after "## Citations"
    // skipping the first line so we don't match the same heading again
    const subsequentHeading = citationsBlock.slice(2).search(/\n#{1,6}\s+\w/)
    if (subsequentHeading > -1) {
      // cut off the block at that heading
      citationsBlock = citationsBlock.slice(0, subsequentHeading + 2)
    }
  
    // Now we have the citations block, which hopefully has bullet lines
    // Convert to lines, skip the first line (which is "## Citations")
    const lines = citationsBlock.split('\n').slice(1)
    console.log('[DeepResearch] citationsBlock lines:', lines)
  
    // We'll filter lines starting with "* " or "- "
    // If your bullets differ, adjust.
    let bulletLines = lines.map(l => l.trim()).filter(l => {
      return l.startsWith('*') || l.startsWith('-')
    })
    console.log('[DeepResearch] bulletLines after filter:', bulletLines)
  
    // Let's parse out the URL if present
    // We'll produce an array of { id, title, url }
    let idCounter = 1
    const parsed = bulletLines.map(line => {
      // remove leading "* " or "- "
      line = line.replace(/^(\*|-)\s*/, '').trim()
  
      // naive approach: search for URL with regex
      const urlMatch = line.match(/(https?:\/\/[^\s]+)/)
      let url = ''
      if (urlMatch) {
        url = urlMatch[0]
      }
  
      // remove the URL from the line
      let title = line.replace(url, '').trim()
      // remove trailing colon if any
      title = title.replace(/:\s*$/, '').trim()
      if (!title) {
        title = 'Untitled citation'
      }
  
      return {
        id: idCounter++,
        title,
        url
      }
    })
  
    console.log('[DeepResearch] Parsed citations:', parsed)
    return parsed
  })
  
  // ---- CITATION PAGINATION & SEARCH ----
  const pageSize = 6
  const currentPage = ref(1)
  const searchQuery = ref('')
  
  const filteredCitations = computed(() => {
    if (!searchQuery.value) return citations.value
    const q = searchQuery.value.toLowerCase()
    return citations.value.filter(cit => {
      return cit.title.toLowerCase().includes(q) || cit.url.toLowerCase().includes(q)
    })
  })
  
  const totalCitationsCount = computed(() => citations.value.length)
  const totalPages = computed(() => {
    const total = filteredCitations.value.length
    return total > 0 ? Math.ceil(total / pageSize) : 1
  })
  
  const pagedCitations = computed(() => {
    if (currentPage.value > totalPages.value) currentPage.value = totalPages.value
    const start = (currentPage.value - 1) * pageSize
    const end = start + pageSize
    return filteredCitations.value.slice(start, end)
  })
  
  function nextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }
  function prevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }
  
  // ---- HELPERS: FAVICON & DOMAIN ----
  function getFavicon(url) {
    if (!url) return 'https://via.placeholder.com/64?text=No+URL'
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
    } catch {
      return 'https://via.placeholder.com/64?text=Err'
    }
  }
  function getDomain(url) {
    if (!url) return ''
    try {
      return new URL(url).hostname.replace(/^www\./, '')
    } catch {
      return url
    }
  }
  
  // ---- Optional onMounted debug ----
  onMounted(() => {
    console.log('[DeepResearch] finalReport text (after removing Citations):', finalReport.value)
  })
  
  </script>
  
  <style scoped>
  .deep-research {
    /* Container styling, adjust as needed */
  }
  
  /* Basic Markdown styling tweaks */
  .report-content :deep(h1) {
    @apply text-3xl font-bold mt-6 mb-4;
  }
  .report-content :deep(h2) {
    @apply text-2xl font-bold mt-6 mb-3;
  }
  .report-content :deep(h3) {
    @apply text-xl font-semibold mt-4 mb-2;
  }
  .report-content :deep(p) {
    @apply text-base leading-relaxed mb-3 text-gray-800 dark:text-gray-200;
  }
  .report-content :deep(a) {
    @apply text-blue-600 dark:text-blue-400 underline;
  }
  
  /* Citation card styling */
  .citation-card {
    @apply relative;
  }
  .citation-card:hover {
    @apply shadow-md;
  }
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  </style>
  