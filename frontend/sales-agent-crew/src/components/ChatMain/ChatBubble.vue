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
       
                <!-- Card Section -->
<div class="w-100  mx-auto">
  <!-- Grid -->
  <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
    <!-- Card -->
    <a  v-for="(item, index) in workflowData" :key="index"    class="group flex flex-col bg-primary-brandDarkGray border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800" href="#">
      <div class="p-4 md:p-5">
        <div class="flex gap-x-5">
          <!-- <svg class="mt-1 shrink-0 size-5 text-gray-800 dark:text-neutral-200" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> -->

          <div class="grow">
            <h3 class="group-hover:text-blue-600  text-gray-800 dark:group-hover:text-neutral-400 dark:text-neutral-200">
              {{item.llm_name}}
            </h3>
            <p class="text-sm text-gray-500 dark:text-neutral-500">
             <span>{{ item.llm_provider }} </span>  <span v-if="item.duration">{{ formattedDuration(item.duration) }} </span> 
            </p>
          </div>
        </div>
      </div>
    </a>
   </div>
</div>
<!-- End Card Section -->
          
            <div v-if="plannerText">
          <div   @click="isOpen = !isOpen"  class="flex items-center">
            <span>Analysis Concluded(<span class="text-sm"  v-if="!isLoading">{{ formattedDuration(parsedData.metadata.duration)}}s</span>):</span>
        
            <br/>
            
            <span><svg
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
        </span>
          </div>
          
           <!-- Corrected directive: v-if not v:if -->
           <div v-if="isOpen">  
            {{ plannerText }}
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



  const formattedDuration=(duration) =>{
      // Format duration to 2 decimal places
      return duration.toFixed(2);
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
        
  workflowData: {
    type: [],
    required: false // Ensure it's always provided
  },
  
  })
  
  
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
  
  </script>
  