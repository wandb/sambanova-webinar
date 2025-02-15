<template>
    <div>
      <p>Unknown agent type: {{ parsed.agent_type }}</p>
      <p> {{ parsed.data?.response }}</p>
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
  