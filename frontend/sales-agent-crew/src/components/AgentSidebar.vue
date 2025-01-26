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
    console.log('[AgentSidebar] Missing userId or runId:', { userId: props.userId, runId: props.runId })
    return
  }

  // Close existing connection
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''
  const url = `${baseUrl}/stream/logs?user_id=${props.userId}&run_id=${props.runId}`
  console.log('[AgentSidebar] Connecting to SSE:', url)

  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    try {
      console.log('[AgentSidebar] Raw SSE event data:', event.data)
      const data = JSON.parse(event.data)
      console.log('[AgentSidebar] Parsed SSE message:', data)

      // If it's a "connection_established" or "ping" message, skip
      if (data.type === 'connection_established') {
        console.log('[AgentSidebar] SSE connection established')
        return
      }
      if (data.type === 'ping') {
        // Keep-alive message
        return
      }

      // Normal agent message
      let messageData = data
      if (!messageData.user_id || !messageData.run_id || !messageData.agent_name) {
        console.log('[AgentSidebar] message missing fields', messageData)
        return
      }

      // Check if the message matches the current user/run
      if (
        messageData.user_id === props.userId &&
        messageData.run_id === props.runId
      ) {
        // Clean up text (remove excessive newlines, etc.)
        let cleanText = messageData.text
          .replace(/\n{3,}/g, '\n\n')
          .replace(/You ONLY have access.*$/s, '')
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
      } else {
        console.log('[AgentSidebar] SSE message does not match userId/runId, ignoring')
      }
    } catch (err) {
      console.error('[AgentSidebar] Error parsing SSE message:', err, 'Raw event data:', event.data)
    }
  }

  eventSource.onerror = (err) => {
    console.error('[AgentSidebar] SSE connection error:', err)
    // If the connection closes, attempt to reconnect after 5s
    if (eventSource.readyState === EventSource.CLOSED) {
      console.log('[AgentSidebar] SSE readyState=CLOSED, reconnecting in 5s')
      setTimeout(() => {
        connectToSSE()
      }, 5000)
    }
  }

  eventSource.onopen = () => {
    console.log('[AgentSidebar] SSE connection opened successfully')
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
