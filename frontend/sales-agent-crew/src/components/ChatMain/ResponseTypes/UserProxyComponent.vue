<template>
    <div class="user-proxy-message">
      
      <p>{{ parsed.data?.agent_question || parsed.data?.deep_research_question }}</p>
      <!-- You might also parse parsed.message if needed -->
    </div>
  </template>
  
  <script setup>
  const props = defineProps({
    parsed: {
      type: Object,
      required: true
    }
  });
  </script>
  