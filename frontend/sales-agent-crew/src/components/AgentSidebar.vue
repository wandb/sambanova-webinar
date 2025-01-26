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
          <div class="flex justify-between items-center mb-1">
            <div class="text-xs text-gray-500">{{ msg.agent_name }}</div>
            <div class="text-xs text-gray-400">
              {{ new Date(msg.timestamp * 1000).toLocaleTimeString() }}
            </div>
          </div>
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
    if (!props.userId || !props.runId) {
        console.log('Missing userId or runId:', { userId: props.userId, runId: props.runId })
        return
    }

    // Close existing connection
    if (eventSource) {
        eventSource.close()
        eventSource = null
    }

    const url = `${import.meta.env.VITE_API_URL}/stream/logs?user_id=${props.userId}&run_id=${props.runId}`
    console.log('Connecting to SSE:', url)
    eventSource = new EventSource(url)

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data)
            console.log('Received SSE message:', data)

            // Skip connection established message
            if (data.type === 'connection_established') {
                console.log('Connection established message received')
                return
            }

            // Skip ping messages
            if (data.type === 'ping') {
                return
            }

            // For actual agent messages, parse the JSON string if needed
            let messageData = data
            if (typeof data === 'string') {
                messageData = JSON.parse(data)
            }

            // Only add messages that have agent_name and text
            if (messageData.agent_name && messageData.text) {
                // Clean up the text by removing excessive newlines and tool instructions
                let cleanText = messageData.text
                    .replace(/\n{3,}/g, '\n\n')  // Replace 3+ newlines with 2
                    .replace(/You ONLY have access.*$/s, '')  // Remove tool instructions
                    .trim()

                messages.value.push({
                    agent_name: messageData.agent_name,
                    text: cleanText,
                    timestamp: messageData.timestamp
                })

                // Auto-scroll to the bottom
                setTimeout(() => {
                    const container = document.querySelector('.overflow-auto')
                    if (container) {
                        container.scrollTop = container.scrollHeight
                    }
                }, 100)
            }
        } catch (err) {
            console.error('Error parsing SSE message:', err, 'Raw event data:', event.data)
        }
    }

    eventSource.onerror = (err) => {
        console.error('SSE connection error:', err)
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log('Connection closed, attempting to reconnect...')
            setTimeout(() => {
                console.log('Attempting to reconnect...')
                connectToSSE()
            }, 5000)
        }
    }

    eventSource.onopen = () => {
        console.log('SSE connection opened successfully')
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
  