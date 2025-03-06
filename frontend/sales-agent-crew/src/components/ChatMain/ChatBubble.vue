<template>
    <!-- Check if event is 'user_message' -->
    <li
      v-if="props.event === 'user_message'" 
      class=" flex  px-4 items-start    gap-x-2 sm:gap-x-4"
    >
    
      <div class="grow text-end space-y-3 ">
        <!-- Card -->
        <div class="inline-block flex justify-end ">
          <p class="text-[16px]  text-left color-primary-brandGray max-w-[80%] w-auto">
            {{ props.data }}
            
          </p>
        </div>
        <!-- End Card -->
      </div>
      <UserAvatar :type="user" />
    </li>
    
    <!-- For all other cases -->
    <li v-else class="  relative  px-4 items-start gap-x-2 sm:gap-x-4">
      {{ (props.data?.data) }}
      <div class="w-full relative flex items-center  ">
    
        <UserAvatar :type="provider" />   
        <div class="grow relative text-start space-y-3">
        <!-- Card -->
        <div class="inline-block" >
       <div class="relative p-4 flex items-center capitalize space-y-3 font-inter font-semibold 
       text-[16px] leading-[18px] tracking-[0px] text-center">{{ provider }} Agent   <!-- Menu button: visible on hover -->
      <button
        type="button"
        class=" hidden group-hover:opacity-100 transition-opacity duration-200"
        @click.stop="toggleMenu"
        @mousedown.stop
        aria-label="Open menu"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="5" r="1" />
          <circle cx="12" cy="12" r="1" />
          <circle cx="12" cy="19" r="1" />
        </svg>
      </button>
    
      <!-- Popover menu -->
      <div
        v-if="activeMenu"
        class="absolute right-1 top-8 bg-white border border-gray-200 shadow-lg rounded z-30"
        @click.stop
      >
       
        <button
          class="flex items-center w-full px-4 py-2 hover:bg-gray-100 text-left"
          
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7" />
            <polyline points="12 3 12 12" />
            <polyline points="9 6 12 3 15 6" />
          </svg>
          View Report
        </button>
        <button
          class="flex items-center w-full px-4 py-2 hover:bg-gray-100 text-left"
          @click="genPDF"
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download PDF
        </button>
      </div></div>
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
  import {downloadPDF, generatePDFDeepResearch} from '@/utils/createPDF';



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

const activeMenu = ref(false);

const headerConfig = {
    SVGComponent: SILogo, // Pass Vue Component here
    topHeading: 'Research Report',
    subHeading: 'Generated with Vue 3'
  };

async function genPDF() {
  try {
  //   const sampleContent = {
  //   report: [
  //     {
  //       title: 'Introduction',
  //       high_level_goal: 'Understand the basics of Vue 3',
  //       why_important: 'Vue 3 is a modern framework with reactivity features.',
  //       generated_content: '## Vue 3 Overview\nVue 3 introduces Composition API, better performance, and more...'
  //     }
  //   ]
  // };

  let dataForPdf=JSON.parse(props.data)
console.log(JSON.parse(props.data).data)

if(dataForPdf.agent_type==="deep_research")
generatePDFDeepResearch( JSON.parse(props.data).data , headerConfig);

else if (dataForPdf.agent_type==="deep_research")
generatePDFDeepResearch( JSON.parse(props.data).data , headerConfig);


  }catch(e){
console.log("PDF gen error",e)
  }
}

function toggleMenu() {
    activeMenu.value = !activeMenu.value;
  }
  </script>
  <style>

</style>