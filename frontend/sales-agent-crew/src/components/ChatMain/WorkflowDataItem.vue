<template>
    <div 
      v-for="(item, index) in workflowData" 
      :key="index" 
      class="group flex flex-col bg-primary-brandDarkGray border border-primary-brandGray shadow-sm rounded-xl hover:shadow-md focus:outline-none focus:shadow-md transition dark:bg-neutral-900 dark:border-neutral-800"
    >
      <div class="px-4 py-2 md:px-5">
        <div class="flex items-start relative justify-between">
          <!-- Left: Text Content -->
          <div class="grow">
            <h3 class="text-sm text-primary-bodyText flex items-center">
              <span class="inline-block w-[70%] truncate">
                {{ item.llm_name }}
              </span>
              <span class="ml-1">
                ({{ item.count }})
              </span>
            </h3>
            <p class="text-sm text-gray-500 flex justify-between dark:text-neutral-500">
              <span class="capitalize">{{ item.task }}</span>
              <span v-if="item.duration">{{ formattedDuration(item.duration) }}</span>
            </p>
          </div>
          <!-- Right: Icon  -->
          <div class="absolute top-[5px] right-[5px]">
            <template v-if="item.llm_name.toLowerCase().includes('meta')">
              <img class="size-[16px]" src="/Images/icons/meta.png" alt="">
            </template>
            <template v-else-if="item.llm_name.toLowerCase().includes('deepseek')">
              <img class="size-[16px]" src="/Images/icons/deepseek.png" alt="">
            </template>
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
    isLoading: {
      type: Boolean,
      default: false
    }
  })
  
  const workflowData = props.workflowData
  </script>
  