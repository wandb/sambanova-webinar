<template>
    <div 
      v-for="(item, index) in workflowData" 
      :key="index" 
      class="group flex flex-col bg-primary-brandDarkGray border border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800"
    >
      <div class="px-4 py-2 md:px-5">
        <div class="flex gap-x-5">
          <div class="grow">
            <h3 class="text-sm   text-primary-bodyText">
              {{ item.llm_name }} ({{ item.count }})
            </h3>
            <p class="text-sm text-gray-500 flex justify-between dark:text-neutral-500">
              <span class="capitalize">{{ item.task }}</span>
              <span v-if="item.duration">{{ formattedDuration(item.duration) }}</span>
            </p>
          </div>
        </div>
      </div>
      <div v-if="isLoading" class="mt-1 w-full h-1 bg-gray-300 dark:bg-gray-700 overflow-hidden relative">
        <div class="absolute top-0 left-0 h-full bg-primary-brandPrimaryColor dark:bg-blue-400 animate-loader"></div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue'
  import { formattedDuration } from '@/utils/globalFunctions'
  
  const props = defineProps({
    workflowData: {
      type: Array,
      default: () => []
    },
    isLoading:{
        isLoading:Boolean,
        default:false
    }
  })
  
  // Optionally alias the prop for easier access.
  const workflowData = props.workflowData
  </script>
  