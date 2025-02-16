<template>
  <div class="parsed-content">
    <!-- Loop over each parsed section -->
    <div v-for="(section, index) in sections" :key="index" class="section mb-4">
      <!-- Section Title -->
      <h3 v-if="section.title" class="section-title mb-1">{{ section.title }}</h3>
      <!-- Generated Content rendered as markdown -->
      <div class="section-content text-sm" v-html="renderMarkdown(section.content)"></div>
      
      <!-- Optional: high-level goal -->
      <div v-if="section.high_level_goal" class="mt-2 text-sm text-gray-700">
        <strong>Goal:</strong> {{ section.high_level_goal }}
      </div>
      
      <!-- Optional: why important -->
      <div v-if="section.why_important" class="mt-2 text-sm text-gray-700">
        <strong>Why Important:</strong> {{ section.why_important }}
      </div>
      
      <!-- Optional: content outline -->
      <div v-if="section.content_outline && section.content_outline.length" class="mt-2 text-sm text-gray-700">
        <strong>Outline:</strong>
        <ul class="list-disc ml-4">
          <li v-for="(item, i) in section.content_outline" :key="i">{{ item }}</li>
        </ul>
      </div>
      
      <!-- Optional: sources (rendered as clickable links) -->
      <div v-if="section.sources && section.sources.length" class="mt-2 text-sm text-gray-700">
        <strong>Sources:</strong>
        <ul class="list-disc ml-4">
          <li v-for="(link, i) in section.sources" :key="i">
            <a :href="link" target="_blank" rel="noopener noreferrer" class="text-blue-500 underline">
              {{ link }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'
import { marked } from 'marked'

// Configure marked with a custom renderer to make links clickable.
const renderer = new marked.Renderer()
renderer.link = (href, title, text) => {
  return `<a href="${href}" target="_blank" rel="noopener noreferrer">${text || href}</a>`
}
marked.use({ renderer, gfm: true, breaks: true })

// Declare a prop "parsed" which may be a string or an object.
const props = defineProps({
  parsed: {
    type: [String, Object],
    required: true
  }
})

// Helper: parse the input data. If it's a string, try to JSON.parse it.
function parseData(input) {
  if (typeof input === 'string') {
    try {
      return JSON.parse(input)
    } catch (e) {
      // Not valid JSON, so treat as raw text.
      return { text: input }
    }
  }
  return input
}

const parsedData = computed(() => parseData(props.parsed))

// Compute sections: if parsedData has data.sections, use that; otherwise, fall back to parsing raw text.
const sections = computed(() => {
  if (parsedData.value.data && Array.isArray(parsedData.value.data.sections)) {
    return parsedData.value.data.sections.map(sec => ({
      title: sec.title || '',
      content: sec.generated_content || '',
      high_level_goal: sec.high_level_goal || '',
      why_important: sec.why_important || '',
      content_outline: sec.content_outline || [],
      sources: sec.sources || []
    }))
  } else if (parsedData.value.text) {
    return parseSections(parsedData.value.text)
  }
  return []
})

// Fallback parser for raw text: splits text into sections using "Thought:" or "Final Answer:" as headings.
function parseSections(text) {
  const lines = text.split('\n')
  const sections = []
  let currentSection = { title: '', content: '' }
  for (let line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    const match = trimmed.match(/^(Thought|Final Answer):\s*(.*)$/i)
    if (match) {
      if (currentSection.title || currentSection.content) {
        sections.push({
          title: currentSection.title,
          content: currentSection.content.trim()
        })
      }
      currentSection = { title: match[1].trim(), content: match[2] + "\n" }
    } else {
      currentSection.content += line + "\n"
    }
  }
  if (currentSection.title || currentSection.content) {
    sections.push({
      title: currentSection.title,
      content: currentSection.content.trim()
    })
  }
  return sections
}

// Render markdown to HTML using marked.
function renderMarkdown(text) {
  return marked(text || '')
}
</script>

<style scoped>
.parsed-content {
  font-family: sans-serif;
}
.section {
  margin-bottom: 1rem;
}
.section-title {
  font-weight: bold;
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}
.section-content {
  font-size: 1rem;
  line-height: 1.5;
}
</style>
