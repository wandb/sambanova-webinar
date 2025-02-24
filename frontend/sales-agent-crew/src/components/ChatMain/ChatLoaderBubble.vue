<template>
       <li  
      class="flex py-2 px-4 items-start gap-x-2 sm:gap-x-4">
      <!-- v-else for all other cases -->
      <div class="flex items-start space-x-3">
        <div class="flex-none ">
        <SILogo />
      </div>
        <div class="flex-1 bg-white border border-gray-200 rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
        
          <div v-if="workflowData.length>0" class="w-100  mx-auto">
  <!-- Grid -->
    <!-- Card -->
    <div class="flex my-2">
      <!-- Flex container to arrange items horizontally without forcing full width -->
    <div class="flex space-x-4">
   
    <WorkflowDataItem :isLoading="isLoading" :workflowData="workflowData"/>
  </div>
  </div>
      </div>
     
<!-- End Card Section -->
          <StatusText   :text="statusText"  /> 
          
          <div v:if="isOpen">  {{plannerText}}</div>
        
     

      
      </div>
      </div>
    </li>
    
  </template>
  
  <script setup>

  import SILogo from '@/components/icons/SILogo.vue'
  import StatusText from '@/components/Common/StatusText.vue'
  import HorizontalScroll from '@/components/Common/UIComponents/HorizontalScroll.vue'
  import WorkflowDataItem from '@/components/ChatMain/WorkflowDataItem.vue'


  // Define props
  const props = defineProps({
    plannerText: {
    type: String,
    required: true // Ensure it's always provided
  },
  statusText: {
    type: String,
    required: true // Ensure it's always provided
  },
  
  isOpen: {
    type: Boolean,
    required: true // Ensure it's always provided
  },
    
  workflowData: {
    type: [],
    required: false // Ensure it's always provided
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