<template>
  
          <div class="mt-2 "  @click="isOpen = !isOpen"  >
          <div class="flex justify-between items-center cursor-pointer "
          >
            <div class="flex items-start flex-1 no-wrap">
              <CorrectIcon class="mr-1 flex-shrink-0" />
              <span class=" text-primary-brandTextSecondary font-semibold text-sm">
                <!-- {{ title }} -->
                {{ formatKey(heading) }}
              
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
          <div class="m-1 p-1 border rounded-md bg-primary-brandGray"  v-show="isOpen">
            <div v-if="isObject(value) && !Array.isArray(value)">
        <table class="w-90 border  divide-y divide-gray-200">
          <!-- <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
            </tr>
          </thead> -->
          <tbody class=" divide-y divide-gray-200">
            <tr v-for="(val, key) in value" :key="key">
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">{{ formatKey(key) }}</td>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">

                <!-- {{val}} -->
                <!-- Recursively display each nested value -->
                <RecursiveDisplay :value="val" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- If value is an array, render as a bullet list -->
      <div v-else-if="Array.isArray(value)">
        <ul class="list-disc ml-6 space-y-1">
          <li v-for="(item, index) in value" :key="index">
            <RecursiveDisplay :value="item" />
          </li>
        </ul>
      </div>
  
      <!-- Otherwise, render as plain text -->
      <div v-else>
        <p class="text-sm">{{ value }}</p>
      </div>
          </div>
        </div>
        
  </template>
  
  <script setup>
  import { computed, ref, h, defineComponent, watch } from 'vue'
  import CorrectIcon from '@/components/icons/CorrectIcon.vue'
  import RecursiveDisplay from './RecursiveDisplay.vue'
  // State for accordion toggle (single toggle used for all sections in this example)
  const isOpen = ref(false);
  
  // Define props for TimelineItem
  const props = defineProps({
    data: {
      type: Object,
      required: true
    },
    heading: {
      type: String,
      required: true
    },
    value: {
      type: null,
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


  function isObject(val) {
    return val !== null && typeof val === 'object'
  }

  function formatKey(key) {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
  </script>
  
  <style scoped>
  /* Adjust styles as needed */
  .timeline-item {
    background-color: #fff;
  }
  </style>