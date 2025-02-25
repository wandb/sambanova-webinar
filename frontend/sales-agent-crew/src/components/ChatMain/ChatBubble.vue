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
        <div class="flex-1 bg-white  p-4 space-y-3 ">
       
          
          <AnalysisTimeline 
      :isLoading="isLoading" 
      :parsedData="parsedData" 
      :workflowData="workflowData" 
      :presentMetadata="presentMetadata" 
      :plannerText="plannerText" 
    />
   
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
  import ErrorComponent from '@/components/ChatMain/ResponseTypes/ErrorComponent.vue'
import MetaData from '@/components/ChatMain/MetaData.vue'
import WorkflowDataItem from '@/components/ChatMain/WorkflowDataItem.vue'
import AnalysisTimeline from '@/components/ChatMain/AnalysisTimeline.vue'



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
      case 'error':
        return ErrorComponent
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

</style>