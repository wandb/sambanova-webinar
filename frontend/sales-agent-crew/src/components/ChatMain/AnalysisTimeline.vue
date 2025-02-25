<template>
    <div class="vertical-timeline">
      <!-- Timeline Header -->
      <div class="timeline-header flex items-center justify-start">
        <StatusText :text="statusText" />
        <h2 v-if="!isLoading" class="text-md text-primary-brandTextSecondary">
          Analysis Concluded (<span class="text-sm">{{ formattedDuration(parsedData?.metadata?.duration) }}s</span>)
        </h2>
        <h2 v-if="isLoading" class="text-md text-primary-brandTextSecondary">
          <StatusText :text="statusText" />
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
        <!-- Animated Vertical Line -->
        <div :key="plannerText" class="timeline-line absolute top-0 left-0 h-full w-[2px] bg-primary-timeLine"></div>
        
        <!-- Card Section -->
        <div v-if="workflowData && workflowData.length > 0" class="w-100 mx-auto">
          <div class="flex my-2">
            <div class="flex space-x-4">
              <WorkflowDataItem :workflowData="workflowData" />
            </div>
          </div>
        </div>
        <!-- Inline metadata items -->
        <MetaData v-if="presentMetadata" :presentMetadata="presentMetadata" />
        <!-- Planner text -->
        <div class="markdown-content text-[#667085]" v-html="formattedText(plannerText)"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import WorkflowDataItem from '@/components/ChatMain/WorkflowDataItem.vue'
  import MetaData from '@/components/ChatMain/MetaData.vue'
  import StatusText from '@/components/Common/StatusText.vue'
  import { formattedText } from '@/utils/formatText'
  
  const props = defineProps({
    isLoading: { type: Boolean, default: false },
    parsedData: { type: Object, default: () => ({}) },
    workflowData: { type: Array, default: () => [] },
    presentMetadata: { type: [Object, Array], default: null },
    plannerText: { type: String, default: '' },
    statusText: { type: String, default: '' },
    defaultCollapsed: { type: Boolean, default: true }
  });
  
  const collapsed = ref(props.defaultCollapsed || false);
  function toggleCollapse() {
    collapsed.value = !collapsed.value;
  }
  function formattedDuration(duration) {
    if (typeof duration !== 'number' || isNaN(duration)) return duration;
    return duration.toFixed(2);
  }
  </script>
  
  <style scoped>
  .vertical-timeline {
    border-radius: 0.5rem;
    overflow: hidden;
  }
  .timeline-header { }
  .toggle-btn {
    transition: color 0.3s ease;
  }
  .timeline-body {
    transition: all 0.3s ease;
  }
  
  /* Animate the vertical line with a bounce effect */
  .timeline-line {
    transform-origin: top;
    transform: scaleY(0);
    /* Animate over 1s with a bounce effect */
    animation: growLine 1s cubic-bezier(0.2, 1, 0.3, 1) forwards;
  }
  
  @keyframes growLine {
    0% {
      transform: scaleY(0);
    }
    60% {
      transform: scaleY(1.1);
    }
    80% {
      transform: scaleY(0.95);
    }
    100% {
      transform: scaleY(1);
    }
  }
  </style>
  