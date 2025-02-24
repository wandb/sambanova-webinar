<template>
    <!-- Check if event is 'user_message' -->
    <li
      v-if="props.event === 'user_message'" 
      class="py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4"
    >
      <div class="grow text-end space-y-3">
        <!-- Card -->
        <div class="inline-block bg-primary-bodyBg border-primary-brandFrame border rounded-lg p-4 shadow-sm">
          <p class="text-sm color-primary-brandGray">
            {{ props.data }}
          </p>
        </div>
        <!-- End Card -->
      </div>
      <UserAvatar />
    </li>
    
    <!-- For all other cases -->
    <li v-else class="flex py-2 px-4 items-start gap-x-2 sm:gap-x-4">
      <div class="flex-none ">

        <SILogo />
        </div>
        <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
       
          <div class="vertical-timeline">
    <!-- Timeline Header -->
    <div class="timeline-header flex items-center justify-start  ">
      <h2 class="text-md text-primary-brandTextSecondary ">Analysis Concluded (<span class="text-sm"  v-if="!isLoading">{{ formattedDuration(parsedData.metadata?.duration)}}s</span>)</h2>
      <button @click="toggleCollapse" class="toggle-btn flex items-center text-blue-500 hover:text-blue-600 focus:outline-none">
        <!-- <span class="mr-2 text-sm font-medium">{{ collapsed ? 'Expand Timeline' : 'Collapse Timeline' }}</span> -->

        
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
    <!-- Timeline Body (line starts here) -->
    <div v-show="!collapsed" class="timeline-body relative pl-[18px] pt-4 pb-8">
      <!-- Vertical line with gradient -->
      <div class="timeline-line absolute top-0 bottom-0 left-0 w-[2px] bg-primary-timeLine"></div>

                <!-- Card Section -->
<div v-if="workflowData.length>0" class="w-100  mx-auto">
  <!-- Grid -->
    <!-- Card -->
    <div class="flex my-2">
      <!-- Flex container to arrange items horizontally without forcing full width -->
    <div class="flex space-x-4">
      <WorkflowDataItem  :workflowData="workflowData"/>

    </div>
  </div>
   
</div>

 <!-- Inline metadata items with rocket icon -->
<MetaData v-if="presentMetadata" :presentMetadata="presentMetadata"/>
      <!-- Render only available metadata fields -->
     
<!-- End Card Section -->
          
            
       
          
           <!-- Corrected directive: v-if not v:if -->
           <div >  
            {{ plannerText }}
          
        </div>
      </div>
    </div>
        <component :is="selectedComponent" :parsed="parsedData" />
    </div>
      
      
    
    </li>
  </template>
  
  <script setup>
  import { computed, defineProps, ref } from 'vue'
  import SILogo from '@/components/icons/SILogo.vue'
  import UserAvatar from '@/components/Common/UIComponents/UserAvtar.vue'
  import AssistantComponent from '@/components/ChatMain/ResponseTypes/AssistantComponent.vue'
  import UserProxyComponent from '@/components/ChatMain/ResponseTypes/UserProxyComponent.vue'
  import SalesLeadComponent from '@/components/ChatMain/ResponseTypes/SalesLeadsComponent.vue'
  import EducationalComponent from '@/components/ChatMain/EducationalComponent.vue'
  import UnknownTypeComponent from '@/components/ChatMain/ResponseTypes/UnknownTypeComponent.vue'
  import FinancialAnalysisComponent from '@/components/ChatMain/ResponseTypes/FinancialAnalysisComponent.vue'
  import DeepResearchComponent from '@/components/ChatMain/ResponseTypes//DeepResearchComponent.vue'
import MetaData from '@/components/ChatMain/MetaData.vue'
import WorkflowDataItem from '@/components/ChatMain/WorkflowDataItem.vue'



  const formattedDuration=(duration) =>{
      // Format duration to 2 decimal places
      return duration?.toFixed(2);
    }
  
  // Define props
  const props = defineProps({
    data: {
      type: String,
      required: true
    },
    event: {
      type: String,
      required: true
    },
    plannerText: {
      type: String,
      required: true
    },
    statusText: {
      type: String,
      required: true
    },
    isLoading: {
      type: Boolean,
      required: true
    },
    metadata: {
      type: Object,
      required: true
    },
  workflowData: {
    type: [],
    required: false // Ensure it's always provided
  },
  
  })
  

  const presentMetadata = computed(() => {


  if (!props.metadata) return null;

  return props.metadata;
});

  
  // Parse the JSON string safely
  const parsedData = computed(() => {
    try {
      return JSON.parse(props.data)
    } catch (error) {
      console.error('Error parsing data in ChatBubble:', error)
      return {}
    }
  })
  
  // Choose which sub-component to display based on agent_type
  const selectedComponent = computed(() => {
    switch (parsedData.value.agent_type) {
      case 'assistant':
        return AssistantComponent
      case 'educational_content':
        return EducationalComponent
      case 'user_proxy':
        return UserProxyComponent
      case 'sales_leads':
        return SalesLeadComponent
      case 'financial_analysis':
        return FinancialAnalysisComponent
        case 'deep_research':
        return DeepResearchComponent
      default:
        return UnknownTypeComponent
    }
  })
  
  // Define isOpen; if not passed as prop, define it as a ref
  const isOpen = ref(false)  // adjust as needed; for instance, based on statusText or other logic
  const collapsed = ref(true)
function toggleCollapse() {
  collapsed.value = !collapsed.value
}
  </script>
  <style>
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