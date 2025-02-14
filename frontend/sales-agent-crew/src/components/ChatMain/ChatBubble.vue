<template>
      <SILogo />
      <div class="space-y-3">
      <component :is="selectedComponent" :parsed="parsedData" />
    </div>
      <!-- <div class="space-y-3">
        <h2 class="font-medium text-gray-800 dark:text-white">
          {{ parsedResponse.response }}
        </h2>
        <p class="text-sm text-gray-800 dark:text-white">
          Query: {{ parsedMessage.query }}
        </p>
      </div> -->
    
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import SILogo from '@/components/icons/SILogo.vue'
  import AssistantComponent from '@/components/ChatMain/ResponseTypes/AssistantComponent.vue'
import UserProxyComponent from '@/components/ChatMain/ResponseTypes/UserProxyComponent.vue'
import UnknownTypeComponent from '@/components/ChatMain/ResponseTypes/UnknownTypeComponent.vue'
  // The parent passes a JSON string as the "data" prop.
  const props = defineProps({
    data: {
      type: String,
      required: true
    }
  });
  

  
  const parsedData = computed(() => {
  try {
    return JSON.parse(props.data)
  } catch (error) {
    console.error('Error parsing data in ChatBubble:', error)
    return {}
  }
});

// 2. Choose which sub-component to display based on agent_type
const selectedComponent = computed(() => {
  switch (parsedData.value.agent_type) {
    case 'assistant':
      return AssistantComponent
    case 'user_proxy':
      return UserProxyComponent
    // Add cases for other agent types as needed
    default:
      return UnknownTypeComponent
  }
});
  </script>
  