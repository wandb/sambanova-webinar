<template>
    <div class="user-proxy-message">
      
      <p>{{ parsed.data?.user_question }}</p>
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
  