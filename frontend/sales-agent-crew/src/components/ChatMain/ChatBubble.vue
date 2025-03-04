<template>
    <!-- Check if event is 'user_message' -->
    <li
      v-if="props.event === 'user_message'" 
      class=" flex  px-4 items-center  gap-x-2 sm:gap-x-4"
    >
    
      <div class="grow text-end space-y-3">
        <!-- Card -->
        <div class="inline-block  ">
          <p class="text-[16px] color-primary-brandGray">
            {{ props.data }}
            
          </p>
        </div>
        <!-- End Card -->
      </div>
      <UserAvatar :type="user" />
    </li>
    
    <!-- For all other cases -->
    <li v-else class="    px-4 items-start gap-x-2 sm:gap-x-4">
      
      <div class="w-full flex items-center ">
    
        <UserAvatar :type="provider" /> 
        <div class="grow text-start space-y-3">
        <!-- Card -->
        <div class="inline-block" >
       <div class=" p-4 capitalize space-y-3 font-inter font-semibold text-[16px] leading-[18px] tracking-[0px] text-center">{{ provider }} Agent</div>
</div>

</div>
        </div>
        <div class="w-full bg-white  ">
          
          <AnalysisTimeline 
      :isLoading="isLoading" 
      :parsedData="parsedData" 
      :workflowData="workflowData" 
      :presentMetadata="parsedData.metadata" 
      :plannerText="plannerText" 
    />
   
        <component :is="selectedComponent" :parsed="parsedData" />
    </div>
      
      
    
    </li>
  </template>
  
  <script setup>
  import { computed, defineProps, ref,watch } from 'vue'
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
    // statusText: {
    //   type: String,
    //   required: true
    // },
    // isLoading: {
    //   type: Boolean,
    //   required: true
    // },
    metadata: {
      type: Object,
      required: true
    },
    provider: {
      type: String,
      required: true
    },
    messageId: {
      type: String,
      required: true
    },
    
  workflowData: {
    type: [],
    required: false // Ensure it's always provided
  },
  
  })
  const presentMetadata = computed(() => {


if (!parsedData.metadata) return null;

return parsedData.metadata;
});

  const presentMetadataOld = computed(() => {


  if (!props.metadata) return null;

  return props.metadata;
});


// watch(
//   () => props.workflowData,
//   (newWorkflowData, oldWorkflowData) => {
//     console.log("Prop myProp received/changed:", newWorkflowData);
//     // You can add additional checks or logic here
//   },
//   { immediate: true } // This makes sure the watcher fires immediately upon component creation.
// );
  
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