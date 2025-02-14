<template>
    <div class="assistant-message">
      <h3>Assistant Message:</h3>
      <!-- The raw text from data.response -->
      <p>{{ parsed.data?.response }}</p>
      <!-- Possibly parse the nested message if needed -->
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
  