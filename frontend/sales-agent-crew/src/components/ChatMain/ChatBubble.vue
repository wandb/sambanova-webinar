<template>
    
      <!-- Check if event is 'user_input' -->
      <li v-if="props.event == 'user_message'" 
      class=" py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
        <div class="grow text-end space-y-3">
          <!-- Card -->
          <div class="inline-block bg-blue-600 rounded-lg p-4 shadow-sm">
            <p class="text-sm text-white">
                {{ props.data }}
            </p>
          </div>
          <!-- End Card -->
        </div>

        <!-- <span class="shrink-0 inline-flex items-center justify-center size-[38px] rounded-full bg-gray-600">
          <span class="text-sm font-medium text-white leading-none">AZ</span>
        </span> -->
        <UserAvatar />
      </li>
     
      <li   v-else 
      class=" py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4">
      <!-- v-else for all other cases -->
      <div class="flex items-start space-x-3">
        <SILogo />
        <div class="space-y-3">
          <component :is="selectedComponent" :parsed="parsedData" />
        </div>
      </div>
    </li>
    
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import SILogo from '@/components/icons/SILogo.vue'
  import UserAvatar from '@/components/Common/UIComponents/UserAvtar.vue'
  import AssistantComponent from '@/components/ChatMain/ResponseTypes/AssistantComponent.vue'
  import UserProxyComponent from '@/components/ChatMain/ResponseTypes/UserProxyComponent.vue'
  import SalesLeadComponent from '@/components/ChatMain/ResponseTypes/SalesLeadsComponent.vue'
    import EducationalComponent from '@/components/ChatMain/ResponseTypes/EducationalComponent.vue'
  import UnknownTypeComponent from '@/components/ChatMain/ResponseTypes/UnknownTypeComponent.vue'
  import FinancialAnalysisComponent from '@/components/ChatMain/ResponseTypes/FinancialAnalysisComponent.vue'
  
  // Define props
  const props = defineProps({
    data: {
      type: String,
      required: true
    },
    event: {
    type: String,
    required: true // Ensure it's always provided
  },
  
  })
  
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
        
      default:
        return UnknownTypeComponent
    }
  })
  </script>
  