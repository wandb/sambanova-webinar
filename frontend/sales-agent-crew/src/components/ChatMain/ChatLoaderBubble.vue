<template>
       <li  
      class="flex py-2 max-w-4xl px-4 items-start gap-x-2 sm:gap-x-4">
      <!-- v-else for all other cases -->
      <div class="flex items-start space-x-3">
        <div class="flex-none ">
          <UserAvatar :type="provider" />

      </div>
        <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4 space-y-3 ">
        

          <AnalysisTimeline 
      :isLoading="isLoading" 
      :workflowData="workflowData" 
      :plannerText="plannerText" 
      :statusText="statusText"
       :defaultCollapsed="false"
      isOpen="'true'"
    />
     
     
<!-- End Card Section -->
          <!-- <StatusText   :text="statusText"  /> 
          
          <div v:if="isOpen">  {{plannerText}}</div> -->
        
     

      
      </div>
      </div>
    </li>
    
  </template>
  
  <script setup>

import AnalysisTimeline from '@/components/ChatMain/AnalysisTimeline.vue'

  import UserAvatar from '@/components/Common/UIComponents/UserAvtar.vue'


  // Define props
  const props = defineProps({
    plannerText: {
    type: String,
    required: false // Ensure it's always provided
  },
  statusText: {
    type: String,
    required: false // Ensure it's always provided
  },
  
  isLoading: {
    type: Boolean,
    required: false // Ensure it's always provided
  },
   
  workflowData: {
    type: Array,
    required: false // Ensure it's always provided
  },
  provider: {
      type: String,
      required: false
    },
 
  })
  
  
  </script>
  <style>
  @keyframes loaderAnimation {
    0% {
      width: 0%;
    }
    100% {
      width: 100%;
    }
  }
  .animate-loader {
    animation: loaderAnimation 2s linear infinite;
  }
</style>