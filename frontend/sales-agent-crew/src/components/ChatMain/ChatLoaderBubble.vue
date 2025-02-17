<template>
    
     
     
      <li  
      class="max-w-4xl py-2 px-4  flex gap-x-2 sm:gap-x-4">
      <!-- v-else for all other cases -->
      <div class="flex items-start space-x-3">
        <SILogo />
        <div class="bg-white border border-primary-brandFrame  rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
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
  
  })
  
  // Parse the JSON string safely
 
  </script>
  