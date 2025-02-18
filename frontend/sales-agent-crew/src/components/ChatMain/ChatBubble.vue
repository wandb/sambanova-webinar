<template>
  <!-- Check if event is 'user_message' -->
  <li
    v-if="props.event === 'user_message'" 
    class="py-2 px-4 sm:px-6 lg:px-8 mx-auto flex gap-x-2 sm:gap-x-4"
  >
    <div class="grow text-end space-y-3">
      <!-- Card -->
      <div class="inline-block bg-primary-bodyBg border-primary-brandFrame border rounded-lg p-4 shadow-sm">
        <p class="text-sm color-primary-brandGray">
          {{ props.data }}
        </p>
      </div>
      <!-- End Card -->
    </div>
    <UserAvatar />
  </li>
  
  <!-- For all other cases -->
  <li v-else class="max-90 py-2 px-4 flex gap-x-2 sm:gap-x-4">
    <div class="flex items-start space-x-3">
      <SILogo />
      <div class="bg-white border border-primary-brandFrame rounded-lg p-4 space-y-3 dark:bg-neutral-900 dark:border-neutral-700">
        <div v-if="plannerText">
          <div @click="isOpen = !isOpen" class="flex items-center cursor-pointer">
            <span>Analysing:</span>
            <span>
              <svg
                v-if="!isOpen"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600 ml-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600 ml-1 transform rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </span>
          </div>
          <div v-if="isOpen" class="mt-2 text-sm whitespace-pre-wrap">
            {{ plannerText }}
          </div>
        </div>

        <!-- Render our chosen sub-component -->
        <component
          :is="selectedComponent"
          :parsed="parsedData"
        />
      </div>
    </div>
  </li>
</template>

<script setup>
import { computed, defineProps, ref } from 'vue'
import SILogo from '@/components/icons/SILogo.vue'
import UserAvatar from '@/components/Common/UIComponents/UserAvtar.vue'
import AssistantComponent from '@/components/ChatMain/ResponseTypes/AssistantComponent.vue'
import UserProxyComponent from '@/components/ChatMain/ResponseTypes/UserProxyComponent.vue'
import SalesLeadComponent from '@/components/ChatMain/ResponseTypes/SalesLeadsComponent.vue'
import EducationalComponent from '@/components/ChatMain/EducationalComponent.vue'
import UnknownTypeComponent from '@/components/ChatMain/ResponseTypes/UnknownTypeComponent.vue'
import FinancialAnalysisComponent from '@/components/ChatMain/ResponseTypes/FinancialAnalysisComponent.vue'

// NEW: Our Deep Research component
import DeepResearchComponent from '@/components/ChatMain/ResponseTypes/DeepResearchComponent.vue'

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
statusText: {
  type: String,
  required: true
},
isLoading: {
  type: Boolean,
  required: true
}
})

/**
* Attempt to parse the JSON string from props.data 
*/
const parsedData = computed(() => {
try {
  return JSON.parse(props.data)
} catch (error) {
  console.error('Error parsing data in ChatBubble:', error)
  return {}
}
})

/**
* Dynamically choose which sub-component to render 
* based on "agent_type" in the parsed data 
*/
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
  // NEW CASE FOR "deep_research"
  case 'deep_research':
    return DeepResearchComponent
  default:
    return UnknownTypeComponent
}
})

// For expanding/collapsing the "plannerText" (optional logic)
const isOpen = ref(false)

</script>
