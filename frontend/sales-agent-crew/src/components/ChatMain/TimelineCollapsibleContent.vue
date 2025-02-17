<template>
  
          <div class="mt-2"  @click="isOpen = !isOpen"  >
          <div class="flex justify-between items-center cursor-pointer "
          >
            <div class="flex items-start flex-1 no-wrap">
              <CorrectIcon class="mr-1 flex-shrink-0" />
              <span class=" text-primary-brandTextSecondary font-semibold text-sm">
                <!-- {{ title }} -->
                <template v-if="isPrimaryHeading(data.title)">
              <h4 class="font-semibold text-sm break-words">{{ data.title }}
                <template v-if="data.title==='Thought'"><br/>
                <span class=" text-brandTextSecondary font-normal  text-sm">{{data.content }}</span></template></h4> 
              
            </template>
              </span>
            </div>
            <!-- Arrow icon toggles direction based on accordion state -->
            <div v-if="data.title!=='Thought'" class="transition-all duration-300 flex-shrink-0">
              <svg
                v-if="!isOpen"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600 transform rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div v-if="data.title!=='Thought'" v-show="isOpen">
              <div class="mt-1 p-2 border border-primary-brandFrame bg-primary-bodyBg text-sm" v-html="formatContent(data.content || '')"></div>
          </div>
        </div>
        
  </template>
  
  <script setup>
  import { computed, ref, h, defineComponent, watch } from 'vue'
  import CorrectIcon from '@/components/icons/CorrectIcon.vue'
  
  // State for accordion toggle (single toggle used for all sections in this example)
  const isOpen = ref(false);
  
  // Define props for TimelineItem
  const props = defineProps({
    data: {
      type: Object,
      required: true
    },
   
  })
  

  /**
   * Checks if a heading is primary.
   * For this example, only "Thought" and "Final Answer" (case-insensitive) are primary.
   */
  function isPrimaryHeading(title) {
    if (!title) return false
    const lower = title.toLowerCase()
    return lower === 'thought' || lower === 'final answer'
  }
  
  /**
   * Process section content.
   * Replace newline characters with <br> tags.
   */
  function formatContent(content) {
    return content.replace(/\n/g, '<br/>')
  }
  
  /**
   * Parse props.data.text into sections.
   * Only lines starting with "Thought:" or "Final Answer:" (case-insensitive) start new sections.
   * All subsequent lines are appended to that section's content.
   */
  const sections = computed(() => {
    const lines = props.data.text.split('\n')
    const parsed = []
    let currentSection = null
  
    for (let line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      // Check for primary heading pattern
      const match = trimmed.match(/^(Thought|Final Answer|Action Input|Action):\s*(.*)$/i)
      if (match) {
        if (currentSection) {
          currentSection.content = currentSection.content.trim()
          parsed.push(currentSection)
        }
        currentSection = {
          title: match[1].trim(),
          content: match[2] ? match[2].trim() + "\n" : "\n"
        }
      } else {
        if (currentSection) {
          currentSection.content += trimmed + "\n"
        } else {
          // If there's no current section, create one with an empty title
          currentSection = { title: '', content: trimmed + "\n" }
        }
      }
    }
    if (currentSection) {
      currentSection.content = currentSection.content.trim()
      parsed.push(currentSection)
    }
    return parsed
  })
  </script>
  
  <style scoped>
  /* Adjust styles as needed */
  .timeline-item {
    background-color: #fff;
  }
  </style>