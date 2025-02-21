<template>
    
     
     
      <li  
      class=" py-2 px-4  flex gap-x-2 sm:gap-x-4">
      <!-- v-else for all other cases -->
      <div class="flex items-start space-x-3">
        <SILogo />
        <div class="bg-white border border-primary-brandFrame  rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
        
        <!-- Card Section -->
<div class="w-100  mx-auto">
  <!-- Grid -->

  <div class="flex space-x-4">

  <!-- Flex container to arrange items horizontally with min-w-max to prevent shrinkage -->
  <div class="flex space-x-4 min-w-max">
    <a 
      v-for="(item, index) in workflowData" 
      :key="index" 
      class="group flex flex-col bg-primary-brandDarkGray border border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800" 
      href="#"
    >
      <div class="p-4 md:p-5">
        <div class="flex gap-x-5">
          <div class="grow">
            <h3 class="text-sm text-priamry-brandPrimaryColor">
              {{ item.llm_name }}({{ item.count }})
            </h3>
            <p class="text-sm text-gray-500 flex justify-between dark:text-neutral-500">
              <span class="capitalize">{{ item.task }} </span>
              <span v-if="item.duration">{{ formattedDuration(item.duration) }}s</span>
            </p>
          </div>
        
        </div>
      </div>
      <div class="mt-1 w-full h-1 bg-gray-300 dark:bg-gray-700 overflow-hidden relative">
    <div class="absolute top-0 left-0 h-full bg-primary-brandPrimaryColor dark:bg-blue-400 animate-loader"></div>
  </div>
    </a>
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
  
  // Parse the JSON string safely
  const formattedDuration=(duration) =>{
      // Format duration to 2 decimal places
      return duration.toFixed(2);
    }
  
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