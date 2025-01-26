<template>
  <!-- The entire sidebar container; it's collapsible. -->
  <div
    class="border-l border-gray-300 flex flex-col bg-gray-50 transition-all duration-300"
    :class="collapsed ? 'w-12' : 'w-80'"
  >
    <!-- Header area with "Agent Thoughts" title and a toggle button. -->
    <div
      class="flex items-center border-b border-gray-200 p-2 bg-gray-200"
      :class="collapsed ? 'justify-center' : 'justify-between'"
    >
      <!-- Title (hidden when collapsed) -->
      <div
        v-if="!collapsed"
        class="font-bold text-gray-800"
      >
        Agent Thoughts
      </div>

      <!-- Toggle button -->
      <button
        class="hover:bg-gray-300 p-1 rounded"
        @click="collapsed = !collapsed"
      >
        <span v-if="collapsed">
          <!-- Expand icon (arbitrary chevron right) -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 5l7 7-7 7" />
          </svg>
        </span>
        <span v-else>
          <!-- Collapse icon (chevron left) -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 19l-7-7 7-7" />
          </svg>
        </span>
      </button>
    </div>

    <!-- Main content area: scrollable messages -->
    <div
      v-if="!collapsed && userId && runId"
      class="flex-1 overflow-y-auto p-2 space-y-2"
    >
      <!-- Render each parsed message -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="flex flex-col rounded shadow-sm p-2"
        :style="getAgentStyle(msg.agent_name)"
      >
        <!-- Top line => agent name + timestamp -->
        <div class="flex justify-between items-center mb-2">
          <div class="flex items-center space-x-1 font-semibold text-sm">
            <!-- Agent Icon -->
            <span
              v-html="getAgentIcon(msg.agent_name)"
              class="inline-block"
            ></span>
            <span>{{ msg.agent_name }}</span>
          </div>
          <div class="text-xs text-gray-700">
            {{ new Date(msg.timestamp * 1000).toLocaleTimeString() }}
          </div>
        </div>

        <!-- For each "segment" in the parsed message content -->
        <div
          v-for="(segment, idx) in msg.parsedSegments"
          :key="idx"
          class="text-sm text-gray-800 mb-1"
        >
          <!-- Thought block -->
          <div
            v-if="segment.type === 'thought'"
            class="flex items-start space-x-2"
          >
            <span class="font-bold">Thought:</span>
            <div class="whitespace-pre-wrap">{{ segment.content }}</div>
          </div>

          <!-- Action block -->
          <div
            v-else-if="segment.type === 'action'"
            class="flex items-start space-x-2"
          >
            <span class="font-bold text-indigo-700">Action:</span>
            <div class="whitespace-pre-wrap">{{ segment.content }}</div>
          </div>

          <!-- Action Input block -->
          <div
            v-else-if="segment.type === 'action_input'"
            class="flex items-start space-x-2 ml-4"
          >
            <span class="font-bold text-indigo-700">Action Input:</span>
            <pre class="bg-gray-100 p-2 rounded whitespace-pre-wrap text-xs">{{ segment.content }}</pre>
          </div>

          <!-- Observation block -->
          <div
            v-else-if="segment.type === 'observation'"
            class="flex flex-col space-y-1 ml-4"
          >
            <div class="font-bold text-teal-700">Observation:</div>
            <pre class="bg-gray-100 p-2 rounded whitespace-pre-wrap text-xs">{{ segment.content }}</pre>
          </div>

          <!-- Final Answer block -->
          <div
            v-else-if="segment.type === 'final_answer'"
            class="flex flex-col space-y-2"
          >
            <div class="flex items-center space-x-2">
              <span class="font-bold text-purple-700">Final Answer:</span>
              <!-- Toggle to show/hide the final answer details -->
              <button
                class="text-xs text-blue-600 underline"
                @click="segment.show = !segment.show"
              >
                {{ segment.show ? 'Hide' : 'Show' }}
              </button>
            </div>
            <div v-if="segment.show">
              <pre class="bg-white border border-gray-300 rounded p-2 whitespace-pre-wrap text-xs">{{ segment.content }}</pre>
            </div>
          </div>

          <!-- default fallback for lines that don't match known markers -->
          <div v-else class="whitespace-pre-wrap">{{ segment.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'

// PROPS
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

// STATE
const messages = ref([])
let eventSource = null
// The sidebar is initially collapsed => user can expand or it can auto-expand on first message.
const collapsed = ref(true)

// If you want the sidebar to expand automatically on first message, track that:
let firstMessageArrived = false

// RUNTIME
const runIdShort = computed(() => props.runId.slice(0, 8))

/**
 * Agent color & icon map
 */
const agentStyleMap = {
  'Aggregator Search Agent': {
    backgroundColor: '#F3E8FF', // pastel purple
    icon: `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16s1-1 4-1 4 1 4 1 1-1 4-1 4 1 4 1V4H4v12z"/>
      </svg>
    `
  },
  'Data Extraction Agent': {
    backgroundColor: '#E7F9F1', // pastel green
    icon: `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"/>
      </svg>
    `
  },
  'Market Trends Analyst': {
    backgroundColor: '#FFFBEA', // pastel yellow
    icon: `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 3h18v18H3V3zm3 6l3 3-3 3m12-6l-3 3 3 3"/>
      </svg>
    `
  },
  'Outreach Specialist': {
    backgroundColor: '#E7F3FF', // pastel blue
    icon: `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16h6M4 6h16"/>
      </svg>
    `
  }
  // fallback styling can be added for other agent names
}

/**
 * getAgentStyle => returns inline style for background, fallback if no match
 */
function getAgentStyle(agentName) {
  const style = agentStyleMap[agentName]
  return style
    ? { 'background-color': style.backgroundColor }
    : { 'background-color': '#F1F5F9' } // fallback
}

/**
 * getAgentIcon => returns an inline SVG string
 */
function getAgentIcon(agentName) {
  const style = agentStyleMap[agentName]
  return style?.icon || `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 4v16m8-8H4"/>
    </svg>
  `
}

/**
 * parseMessage => Splits the text into segments:
 *   Thought:
 *   Action:
 *   Action Input:
 *   Observation:
 *   Final Answer:
 * We also deduplicate identical final answers.
 */
let lastFinalAnswer = '' // store last final answer to skip duplicates

function parseMessage(fullText) {
  // We separate by possible lines, then re-group
  // We'll build an array of {type, content, show} blocks
  const segments = []
  // We can do a simple approach: find these markers: 
  // "Thought:", "Action:", "Action Input:", "Observation:", "Final Answer:"
  // We'll parse them in order. If none match, it's raw text.

  // Because the text might have multiple lines, let's do a line-based parse.
  let lines = fullText.split('\n')
  let currentType = 'raw'
  let currentContent = ''

  function pushSegment(type, content) {
    // handle final answer dedup
    if (type === 'final_answer') {
      if (content.trim() === lastFinalAnswer.trim()) {
        // skip adding if it's the same exact final answer
        return
      }
      lastFinalAnswer = content.trim()
    }
    segments.push({
      type,
      content,
      // for final answer, hidden by default
      show: (type === 'final_answer') ? false : true
    })
  }

  lines.forEach((line) => {
    const trimmed = line.trim()

    // Check if line starts with these markers:
    if (/^Thought:\s*/i.test(trimmed)) {
      // push any existing content as raw
      if (currentContent.trim()) {
        pushSegment(currentType, currentContent)
      }
      currentType = 'thought'
      currentContent = trimmed.replace(/^Thought:\s*/i, '').trim()
    } else if (/^Action:\s*/i.test(trimmed)) {
      if (currentContent.trim()) {
        pushSegment(currentType, currentContent)
      }
      currentType = 'action'
      currentContent = trimmed.replace(/^Action:\s*/i, '').trim()
    } else if (/^Action Input:\s*/i.test(trimmed)) {
      if (currentContent.trim()) {
        pushSegment(currentType, currentContent)
      }
      currentType = 'action_input'
      currentContent = trimmed.replace(/^Action Input:\s*/i, '').trim()
    } else if (/^Observation:\s*/i.test(trimmed)) {
      if (currentContent.trim()) {
        pushSegment(currentType, currentContent)
      }
      currentType = 'observation'
      currentContent = trimmed.replace(/^Observation:\s*/i, '').trim()
    } else if (/^Final Answer:\s*/i.test(trimmed)) {
      if (currentContent.trim()) {
        pushSegment(currentType, currentContent)
      }
      currentType = 'final_answer'
      currentContent = trimmed.replace(/^Final Answer:\s*/i, '').trim()
    } else {
      // just append to current content
      if (!currentContent) {
        currentContent = trimmed
      } else {
        currentContent += '\n' + trimmed
      }
    }
  })

  // after the loop, push any leftover
  if (currentContent.trim()) {
    pushSegment(currentType, currentContent)
  }

  return segments
}

/**
 * connectToSSE => sets up EventSource, listens for new messages
 */
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

  eventSource.onopen = () => {
    console.log('[AgentSidebar] SSE connection opened successfully')
  }

  eventSource.onerror = (err) => {
    console.error('[AgentSidebar] SSE connection error:', err)
    if (eventSource.readyState === EventSource.CLOSED) {
      console.log('[AgentSidebar] SSE closed, reconnecting in 5s')
      setTimeout(() => {
        connectToSSE()
      }, 5000)
    }
  }

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data.type === 'connection_established') {
        console.log('[AgentSidebar] SSE connection established')
        return
      }
      if (data.type === 'ping') {
        // keep-alive, ignore
        return
      }

      // Normal agent message
      const messageData = data
      if (!messageData.user_id || !messageData.run_id || !messageData.agent_name) {
        console.log('[AgentSidebar] message missing fields => ignoring:', messageData)
        return
      }

      // Check user/run match
      if (messageData.user_id === props.userId && messageData.run_id === props.runId) {
        // If first message => auto expand if collapsed
        if (!firstMessageArrived) {
          firstMessageArrived = true
          collapsed.value = false
        }

        // parse
        let cleaned = messageData.text
          .replace(/\n{3,}/g, '\n\n')
          .replace(/You ONLY have access.*$/s, '')
          .trim()

        const segments = parseMessage(cleaned)

        messages.value.push({
          agent_name: messageData.agent_name,
          timestamp: messageData.timestamp,
          parsedSegments: segments
        })

        // auto scroll
        setTimeout(() => {
          const container = document.querySelector('.overflow-y-auto')
          if (container) {
            container.scrollTop = container.scrollHeight
          }
        }, 100)
      } else {
        console.log('[AgentSidebar] SSE message does not match userId/runId => ignoring')
      }
    } catch (err) {
      console.error('[AgentSidebar] Error parsing SSE message:', err, 'Raw event data:', event.data)
    }
  }
}

/**
 * watch userId/runId => reconnect SSE
 */
watch(
  () => [props.userId, props.runId],
  () => {
    messages.value = []
    lastFinalAnswer = '' // reset final answer dedup
    firstMessageArrived = false
    connectToSSE()
  }
)

// Lifecycle
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
/* Make sure the container can scroll. */
.overflow-y-auto {
  max-height: 100%;
}

/* We can refine the code further if needed. */
</style>
