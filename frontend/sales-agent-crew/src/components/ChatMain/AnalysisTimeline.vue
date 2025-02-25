<template>
    <div class="vertical-timeline">
      <!-- Timeline Header -->
      <div class="timeline-header flex items-center justify-start">
        <h2 class="text-md text-primary-brandTextSecondary">
          Analysis Concluded (<span class="text-sm" v-if="!isLoading">{{ formattedDuration(parsedData?.metadata?.duration) }}s</span>)
        </h2>
        <button @click="toggleCollapse" class="toggle-btn flex items-center text-blue-500 hover:text-blue-600 focus:outline-none">
          <svg v-if="collapsed"
               xmlns="http://www.w3.org/2000/svg"
               class="h-4 w-4 text-[#667085]"
               fill="none"
               viewBox="0 0 24 24"
               stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 9l-7 7-7-7" />
          </svg>
          <svg v-else
               xmlns="http://www.w3.org/2000/svg"
               class="h-4 w-4 text-[#667085] transform rotate-180"
               fill="none"
               viewBox="0 0 24 24"
               stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      <!-- Timeline Body -->
      <div v-show="!collapsed" class="timeline-body relative pl-[18px] pt-4 pb-8">
        <!-- Vertical line with gradient -->
        <div class="timeline-line absolute top-0 bottom-0 left-0 w-[2px] bg-primary-timeLine"></div>
        <!-- Card Section -->
        <div v-if="workflowData && workflowData.length > 0" class="w-100 mx-auto">
          <div class="flex my-2">
            <div class="flex space-x-4">
              <!-- This component is assumed to render each workflow data item -->
              <WorkflowDataItem :workflowData="workflowData"/>
            </div>
          </div>
        </div>
        <!-- Inline metadata items -->
        <MetaData v-if="presentMetadata" :presentMetadata="presentMetadata"/>
        <!-- Planner text -->
        <div>
          {{ plannerText }}
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import WorkflowDataItem from '@/components/ChatMain/WorkflowDataItem.vue'
  import MetaData from '@/components/ChatMain/MetaData.vue'
  
  // Define the props that the timeline will accept.
  const props = defineProps({
    isLoading: { type: Boolean, default: false },
    parsedData: { type: Object, default: () => ({}) },
    workflowData: { type: Array, default: () => [] },
    presentMetadata: { type: [Object, Array], default: null },
    plannerText: { type: String, default: '' }
  });
  
  // Internal state for collapsing the timeline.
  const collapsed = ref(true);
  
  function toggleCollapse() {
    collapsed.value = !collapsed.value;
  }
  
  // Simple duration formatter.
  function formattedDuration(duration) {
    if (typeof duration !== 'number' || isNaN(duration)) return duration;
    return duration.toFixed(2);
  }
  </script>
  
  <style scoped>
  .vertical-timeline {
  /* border: 1px solid #e5e7eb; */
  border-radius: 0.5rem;
  overflow: hidden;
  /* box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); */
  /* background-color: #fff; */
}

.timeline-header {
  /* background-color: #f9fafb; */
}

.toggle-btn {
  transition: color 0.3s ease;
}

.timeline-body {
  transition: all 0.3s ease;
}
.timeline-item:last-child {
  padding-bottom: 0;
}
  </style>
  