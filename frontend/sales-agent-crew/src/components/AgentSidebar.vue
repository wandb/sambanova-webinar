<template>
    <div class="w-80 bg-gray-100 border-l border-gray-300 flex flex-col" v-if="userId && runId">
      <div class="p-2 font-bold bg-gray-200 border-b">
        Agent Thoughts ({{ runIdShort }})
      </div>
      <div class="flex-1 overflow-auto p-2 space-y-2">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          class="bg-white p-2 rounded shadow-sm"
        >
          <div class="text-xs text-gray-500 mb-1">{{ msg.agent_name }}</div>
          <div class="text-sm text-gray-700 whitespace-pre-wrap">
            {{ msg.text }}
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
  
  const props = defineProps({
    userId: {
      type: String,
      default: ''
    },
    runId: {
      type: String,
      default: ''
    }
  })
  
  const messages = ref([])
  let eventSource = null
  
  const runIdShort = computed(() => props.runId.slice(0, 8))
  
  function connectToSSE() {
    if (!props.userId || !props.runId) return
  
    // Close existing connection
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  
    const url = `/stream/logs?user_id=${props.userId}&run_id=${props.runId}`
    eventSource = new EventSource(url)
  
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        messages.value.push(data)
      } catch (err) {
        console.error('Error parsing SSE message:', err)
      }
    }
  
    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err)
      // Optionally handle reconnection, etc.
    }
  }
  
  // Reconnect if userId or runId changes
  watch(
    () => [props.userId, props.runId],
    () => {
      messages.value = []
      connectToSSE()
    }
  )
  
  onMounted(() => {
    connectToSSE()
  })
  
  onBeforeUnmount(() => {
    if (eventSource) {
      eventSource.close()
    }
  })
  </script>
  
  <style scoped>
  /* Basic styling for the right-hand sidebar. */
  </style>
  