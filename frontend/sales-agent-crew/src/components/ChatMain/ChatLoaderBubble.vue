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
  <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
    <!-- Card -->
    <a  v-for="(item, index) in workflowData" :key="index"    class="group flex flex-col bg-primary-brandDarkGray border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800" href="#">
      <div class="p-2 md:p-2">
        <div class="flex gap-x-1">
          <!-- <svg class="mt-1 shrink-0 size-5 text-gray-800 dark:text-neutral-200" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg> -->

          <div class="grow">
            <h3 class="group-hover:text-blue-600  text-gray-800 dark:group-hover:text-neutral-400 dark:text-neutral-200">
              {{item.llm_name}}
            </h3>
            <p class="text-sm text-gray-500 dark:text-neutral-500">
             <span>{{ item.llm_provider }} </span>  <span v-if="item.duration">{{ formattedDuration(item.duration) }}s </span> 
            </p>
          </div>
        </div>
      </div>
    </a>
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
  