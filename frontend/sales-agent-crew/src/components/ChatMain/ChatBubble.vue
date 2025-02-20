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
    <li v-else class="max-90 py-2 px-4 flex gap-x-2 sm:gap-x-4">
      <div class="flex items-start space-x-3">
        <SILogo />
        <div class="bg-white border border-primary-brandFrame rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
       
          <div class="vertical-timeline">
    <!-- Timeline Header -->
    <div class="timeline-header flex items-center justify-start  ">
      <h2 class="text-md font-semibold text-gray-800">Analysis Concluded (<span class="text-sm"  v-if="!isLoading">{{ formattedDuration(parsedData.metadata?.duration)}}s</span>)</h2>
      <button @click="toggleCollapse" class="toggle-btn flex items-center text-blue-500 hover:text-blue-600 focus:outline-none">
        <!-- <span class="mr-2 text-sm font-medium">{{ collapsed ? 'Expand Timeline' : 'Collapse Timeline' }}</span> -->

        
        <svg
          v-if="collapsed"
          class="w-5 h-5 transform"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
        <svg
          v-else
          class="w-5 h-5 transform rotate-180"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>
    <!-- Timeline Body (line starts here) -->
    <div v-show="!collapsed" class="timeline-body relative pl-12 pt-4 pb-8">
      <!-- Vertical line with gradient -->
      <div class="timeline-line absolute top-0 bottom-0 left-4 w-1 bg-gradient-to-b from-orange-500 to-white-500"></div>

                <!-- Card Section -->
<div v-if="workflowData.length>0" class="w-100  mx-auto">
  <!-- Grid -->
    <!-- Card -->
    <div class="flex my-2">
      <!-- Flex container to arrange items horizontally without forcing full width -->
    <div class="flex space-x-4">
      <a 
        v-for="(item, index) in workflowData" 
        :key="index" 
        class="group flex flex-col bg-primary-brandDarkGray border border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800" 
        href="#"
      >
        <div class="p-4 md:p-5">
          <div class="flex gap-x-5">
            <div class="grow">
              <h3 class="group-hover:text-blue-600 text-gray-800 dark:group-hover:text-neutral-400 dark:text-neutral-200">
                {{ item.llm_name }} ({{ item.count }})
              </h3>
              <p class="text-sm text-gray-500 flex justify-between dark:text-neutral-500">
              <span class="capitalize">{{ item.task }} </span>
              <span v-if="item?.duration">{{ formattedDuration(item?.duration) }}s</span>
            </p>
            </div>
          </div>
        </div>
      </a>
    </div>
  </div>
   
</div>

 <!-- Inline metadata items with rocket icon -->
 <div class="flex items-center flex-wrap text-sm text-gray-700">
      <!-- Green Rocket Icon -->
      <svg width="14" height="14" viewBox="0 0 14 14" 
      fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.00016 8.99975C2.44683 8.99975 1.94683 9.22642 1.58683 9.58642C0.800163 10.3731 0.333496 13.6664 0.333496 13.6664C0.333496 13.6664 3.62683 13.1998 4.4135 12.4131C4.7735 12.0531 5.00016 11.5531 5.00016 10.9998C5.00016 9.89308 4.10683 8.99975 3.00016 8.99975ZM3.4735 11.4731C3.28683 11.6598 2.02683 11.9798 2.02683 11.9798C2.02683 11.9798 2.34016 10.7264 2.5335 10.5331C2.64683 10.4064 2.8135 10.3331 3.00016 10.3331C3.36683 10.3331 3.66683 10.6331 3.66683 10.9998C3.66683 11.1864 3.5935 11.3531 3.4735 11.4731ZM10.6135 8.09975C14.8535 3.85975 13.4402 0.559751 13.4402 0.559751C13.4402 0.559751 10.1402 -0.853582 5.90016 3.38642L4.24016 3.05308C3.80683 2.96642 3.3535 3.10642 3.0335 3.41975L0.333496 6.12642L3.66683 7.55308L6.44683 10.3331L7.8735 13.6664L10.5735 10.9664C10.8868 10.6531 11.0268 10.1998 10.9402 9.75975L10.6135 8.09975ZM3.94016 6.21975L2.66683 5.67308L3.98016 4.35975L4.94016 4.55308C4.56016 5.10642 4.22016 5.68642 3.94016 6.21975ZM8.32683 11.3331L7.78016 10.0598C8.3135 9.77975 8.8935 9.43975 9.44016 9.05975L9.6335 10.0198L8.32683 11.3331ZM9.66683 7.15975C8.78683 8.03975 7.4135 8.75975 6.9735 8.97975L5.02016 7.02642C5.2335 6.59308 5.9535 5.21975 6.84016 4.33308C9.96016 1.21309 12.3268 1.67308 12.3268 1.67308C12.3268 1.67308 12.7868 4.03975 9.66683 7.15975ZM9.00016 6.33308C9.7335 6.33308 10.3335 5.73308 10.3335 4.99975C10.3335 4.26642 9.7335 3.66642 9.00016 3.66642C8.26683 3.66642 7.66683 4.26642 7.66683 4.99975C7.66683 5.73308 8.26683 6.33308 9.00016 6.33308Z" fill="#26A69A"/>
</svg>


      <!-- Render only available metadata fields -->
      <template  v-for="(item, index) in presentMetadata" :key="item.key">
        <!-- Add separator dot for every item except the first -->
        <span v-if="index !== 0" class="mx-2 text-xs w-2 h-2 bg-gray-400 rounded-full"></span>
        <span>
          
      
          <strong v-if="item.key==='duration'">{{ formattedDuration(parseFloat(item.value)) }}s</strong>
          <strong v-else>{{ item.value }}s</strong>{{ item.label }} 

        </span>
      </template>
    </div>
<!-- End Card Section -->
          
            
       
          
           <!-- Corrected directive: v-if not v:if -->
           <div >  
            {{ plannerText }}
          
        </div>
      </div>
    </div>
        <component :is="selectedComponent" :parsed="parsedData" />
    </div>
      
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
  import HorizontalScroll from '@/components/Common/UIComponents/HorizontalScroll.vue'



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
      type: Boolean,
      required: true
    },
  workflowData: {
    type: [],
    required: false // Ensure it's always provided
  },
  
  })
  
  const metadata=ref(null)

const presentMetadata = computed(() => {


  if(!metadata) return

  const data = [];

  if (metadata.total_tokens != null) {
    data.push({
      key: 'total_tokens',
      label: 'Total tokens:',
      value: metadata.total_tokens
    });
  }
  if (metadata.prompt_tokens != null) {
    data.push({
      key: 'prompt_tokens',
      label: 'Prompt tokens:',
      value: metadata.prompt_tokens
    });
  }
  if (metadata.cached_prompt_tokens != null) {
    data.push({
      key: 'cached_prompt_tokens',
      label: 'Cached prompt tokens:',
      value: metadata.cached_prompt_tokens
    });
  }
  if (metadata.completion_tokens != null) {
    data.push({
      key: 'completion_tokens',
      label: 'Completion tokens:',
      value: metadata.completion_tokens
    });
  }
  if (metadata.successful_requests != null) {
    data.push({
      key: 'successful_requests',
      label: 'Successful requests:',
      value: metadata.successful_requests
    });
  }
  if (props.metadata.duration != null) {
    data.push({
      key: 'duration',
      label: 'total Duration',
      value: `${metadata.duration}s`
    });
  }
  return data;
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