<template>
  
  <div 
    class="group relative flex p-2">
    <!-- Icon Container (always visible; timeline line is part of this container) -->
    
    <div  class="grow pb-2 group-last:pb-0 min-w-0">
      <!-- Always show period -->
      <h3 :class="collapsed?'justify-center':''" class="mb-1 p-1 truncate text-md  text-primary-brandTextPrimary  flex items-center">
        <div :class="iconContainerClasses" class="color-primary-brandGray flex items-center">
      <component :is="iconComponent"  />
    </div> 
    <span v-if="!collapsed" class="ml-1"> {{ data?.agent_name }}</span>
      </h3>
      <!-- Only show the rest if not collapsed -->
      <div class="ml-2 my-1"    v-for="(section, index) in sections" :key="index" v-if="!collapsed">
        <TimelineCollapsibleContent :data="section" />
      
      </div>
   
    </div>
    <!-- End Right Content -->
  </div>
</template>

<script setup>
import { computed, ref, h, defineComponent, watch } from 'vue'
import CorrectIcon from '@/components/icons/CorrectIcon.vue'
import TimelineCollapsibleContent from '@/components/ChatMain/TimelineCollapsibleContent.vue'
import SearchIcon from '@/components/icons/SearchIcon.vue'
import TechIcon from '@/components/icons/TechIcon.vue'
import SpecialistIcon from '@/components/icons/SpecialistIcon.vue'
import CompetitorIcon from '@/components/icons/CompetitorIcon.vue'
import NewsIcon from '@/components/icons/NewsIcon.vue'
import DataIcon from '@/components/icons/DataIcon.vue'
import RiskIcon from '@/components/icons/RiskIcon.vue'
import TrendsIcon from '@/components/icons/TrendsIcon.vue'
import DefaultIcon from '@/components/icons/DefaultIcon.vue'
import FundamentalIcon from '@/components/icons/FundamentalIcon.vue'
import FinanceIcon from '@/components/icons/FinanceIcon.vue'



// State for accordion toggle (single toggle used for all sections in this example)
const isOpen = ref(false);

// Define props for TimelineItem
const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  isLast: {
    type: Boolean,
    default: false
  }
})

// -------------------------------------------------------------------
// Timeline UI - Icon Container Classes
// -------------------------------------------------------------------
const iconContainerClasses = computed(() => {
  let base =
    "relative after:absolute after:top-8 after:bottom-2 after:start-3 after:w-px after:-translate-x-[0.5px] after:bg-gray-200 dark:after:bg-neutral-700"
  if (props.isLast) {
    base += " after:hidden"
  }
  return base
})


// -------------------------------------------------------------------
// Helper Function: Return a Random Icon Based on Agent Name
// -------------------------------------------------------------------
function getAgentIcon(agentName) {
  console.log("getAgentIcon called for agentName:", agentName)
  const agentIcons = {
    'Competitor Analysis Agent': CompetitorIcon,
   
    'Financial Analysis Agent': FinanceIcon,
    ' Enhanced Competitor Finder Agent': SearchIcon,
    'Aggregator Search Agent': SearchIcon,
    'Fundamental Agent': FundamentalIcon,
    'News Agent': NewsIcon,
    'Technical Agent': TechIcon,
    'Financial Analysis Agent': SearchIcon,
    'Research Agent': SearchIcon,
    'Risk Agent': RiskIcon,
    'Outreach Specialist':  SpecialistIcon,
    'Data Extraction Agent': DataIcon,
    'Market Trends Analyst': TrendsIcon,
  }
  const icon = agentIcons[agentName] || DefaultIcon
  
  console.log("Selected icon:", icon.name)
  return icon
}

// Compute the icon component for this timeline item based on data.agent_name
const iconComponent = computed(() => getAgentIcon(props.data.agent_name))

// -------------------------------------------------------------------
// Text Parsing Helpers
// -------------------------------------------------------------------

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