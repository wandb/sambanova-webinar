<template>
  <!-- This entire sidebar is collapsible. The container must have enough height to scroll internally. -->
  <div class="flex flex-col p-1 overflow-y-auto overflow-x-hidden  border border-primary-brandFrame bg-white rounded-lg h-full border-l  transition-all duration-300 "
  :class="collapsed ? 'w-[64px]  ' : 'w-80'">
      <!-- Collapse/Expand Button -->
      <button
      :class="collapsed?'w-100 h-[36px]  mx-auto':' ' "
        class=" p-2  border-primary-brandFrame mb-2 border flex items-center justify-between border w-full text-center bg-primary-brandGray border-primary-brandGray text-primary-bodyText rounded  text-sm"
        @click="collapsed = !collapsed"
      >
      <span :class="collapsed?'  mx-auto':' ' " class="flex  items-center">
        <span v-if="!collapsed">
          <!-- Expand icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2"
              d="M9 5l7 7-7 7" 
            />
          </svg>
        </span>
        <span :class="collapsed?'  mx-auto':' ' " v-else>
          <!-- Collapse icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2"
              d="M15 19l-7-7 7-7" 
            />
          </svg>
        </span>
        <span v-if="!collapsed" class="ml-2">Agent Reasoning</span>
      </span>
      <span class="hidden" v-if="!collapsed">26 sources</span>
      </button>
      <div>
   
  </div>
 
     <div>



      <TimelineItem  
      v-for="(thought, index) in agentThoughtsData"
      :data="thought"
    period="Researcher"
    title="Search the internet with Exa Search the internet with Exa"
    description="The company has high expectations and using OKRs there is a mutual understanding of expectations and performance."
    :bullets="['Designed template UIs in Figma', 'Converted UIs into responsive HTML/CSS']"
    :iconSvg="getAgentIcon()"
    :collapsed="collapsed"
    :card="{
      href: '#',
      imgSrc: 'https://images.unsplash.com/photo-1661956600655-e772b2b97db4?q=80&w=560&auto=format&fit=crop',
      imgAlt: 'Blog Image',
      title: 'Studio by Mailchimp',
      subtitle: 'Produce professional, reliable streams using Mailchimp.',
    }"
    />



    <template v-if="metadata&&!collapsed">
  <div class="max-w-sm p-4 m-2 bg-[#F9FAFB] border border-gray-200 rounded-lg shadow-sm">
    <!-- Optional Heading -->
    

    <!-- Inline metadata items with rocket icon -->
    <div class="flex items-center flex-wrap text-sm text-gray-700">
      <!-- Green Rocket Icon -->
      <svg width="14" height="14" viewBox="0 0 14 14" 
      fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.00016 8.99975C2.44683 8.99975 1.94683 9.22642 1.58683 9.58642C0.800163 10.3731 0.333496 13.6664 0.333496 13.6664C0.333496 13.6664 3.62683 13.1998 4.4135 12.4131C4.7735 12.0531 5.00016 11.5531 5.00016 10.9998C5.00016 9.89308 4.10683 8.99975 3.00016 8.99975ZM3.4735 11.4731C3.28683 11.6598 2.02683 11.9798 2.02683 11.9798C2.02683 11.9798 2.34016 10.7264 2.5335 10.5331C2.64683 10.4064 2.8135 10.3331 3.00016 10.3331C3.36683 10.3331 3.66683 10.6331 3.66683 10.9998C3.66683 11.1864 3.5935 11.3531 3.4735 11.4731ZM10.6135 8.09975C14.8535 3.85975 13.4402 0.559751 13.4402 0.559751C13.4402 0.559751 10.1402 -0.853582 5.90016 3.38642L4.24016 3.05308C3.80683 2.96642 3.3535 3.10642 3.0335 3.41975L0.333496 6.12642L3.66683 7.55308L6.44683 10.3331L7.8735 13.6664L10.5735 10.9664C10.8868 10.6531 11.0268 10.1998 10.9402 9.75975L10.6135 8.09975ZM3.94016 6.21975L2.66683 5.67308L3.98016 4.35975L4.94016 4.55308C4.56016 5.10642 4.22016 5.68642 3.94016 6.21975ZM8.32683 11.3331L7.78016 10.0598C8.3135 9.77975 8.8935 9.43975 9.44016 9.05975L9.6335 10.0198L8.32683 11.3331ZM9.66683 7.15975C8.78683 8.03975 7.4135 8.75975 6.9735 8.97975L5.02016 7.02642C5.2335 6.59308 5.9535 5.21975 6.84016 4.33308C9.96016 1.21309 12.3268 1.67308 12.3268 1.67308C12.3268 1.67308 12.7868 4.03975 9.66683 7.15975ZM9.00016 6.33308C9.7335 6.33308 10.3335 5.73308 10.3335 4.99975C10.3335 4.26642 9.7335 3.66642 9.00016 3.66642C8.26683 3.66642 7.66683 4.26642 7.66683 4.99975C7.66683 5.73308 8.26683 6.33308 9.00016 6.33308Z" fill="#26A69A"/>
</svg>


      <!-- Render only available metadata fields -->
      <template  v-for="(item, index) in presentMetadata" :key="item.key">
        <!-- Add separator dot for every item except the first -->
        <span v-if="index !== 0" class="mx-2 text-xs w-2 h-2 bg-gray-400 rounded-full"></span>
        <span>
          
      
          <strong v-if="item.key==='duration'">{{ formattedDuration(parseFloat(item.value)) }}s</strong>
          <strong v-else>{{ item.value }}s</strong>{{ item.label }} 

        </span>
      </template>
    </div>
  </div>
</template>



</div>   


  </div>
  <!-- <div v-if="metadata">
  <pre>{{ metadata }}</pre>
</div> -->
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick ,computed} from 'vue'
// import ChatAgentItem from './ChatAgentItem.vue'  
// import AgentTimeline from './AgentTimeline.vue'  
import TimelineItem from '@/components/ChatMain/TimelineItem.vue' 
 
// Reactive variables to store parsed data from the WebSocket.
const agentName = ref('')
const timestamp = ref(0)
const sections = ref([])


// In a real app, these parameters might come from props, route queries, etc.
const userId = ref('')
const conversationId = ref('')

// This ref holds all the log messages concatenated as a single string.
const logs = ref('No data received yet.\n')



// Variable to store the WebSocket instance.
let socket = null

// Function to establish the WebSocket connection.
function connectWebSocket() {

  
  // Construct the base WebSocket URL with /chat endpoint
  let WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000'
  WEBSOCKET_URL = `${WEBSOCKET_URL}/chat`

 
  // Construct the full URL using query parameters.
  const fullUrl = `${WEBSOCKET_URL}?user_id=${props.userId}&conversation_id=${props.runId}`
  console.log('Connecting to:', fullUrl)
  // alert("connectng ",fullUrl)
  socket = new WebSocket(fullUrl)

  socket.onopen = () => {
    console.log('WebSocket connection opened')
    // Log the connection open event.
    logs.value += `Connection opened at ${new Date().toLocaleTimeString()}\n`
    // Send the initial payload.
    const payload = {
      event: "user_input",
      data: "Iphone vs android"
    }
    socket.send(JSON.stringify(payload))
    logs.value += `Sent: ${JSON.stringify(payload)}\n`

  }

  socket.onmessage = (event) => {
    console.log('Received message:', event.data)
    // Append the received data to the log with a newline.
    logs.value += `${event.data}\n`

    try {
      const outerData = JSON.parse(event.data);
      // Parse the inner data string.
      const innerData = JSON.parse(outerData.data);
      // Set agent name and timestamp.
      agentName.value = innerData.agent_name;
      timestamp.value = innerData.timestamp;
      // Parse the text field into sections.
      sections.value = parseSections(innerData.text);
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  }

  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
    logs.value += `Error: ${error.message || 'Unknown error'}\n`
  }

  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event)
    logs.value += `Connection closed at ${new Date().toLocaleTimeString()}\n`
  }
}
// Compute a formatted timestamp (if needed).
const formattedTimestamp = computed(() => {
  if (!timestamp.value) return '';
  return new Date(timestamp.value * 1000).toLocaleString();
});
function parseSections(text) {
  const lines = text.split(/\r?\n/);
  const result = [];
  let currentSection = { heading: '', content: '' };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue; // skip blank lines

    // Check if the line contains a colon in the middle. If the colon is the last character, treat as a heading.
    if (trimmed.endsWith(':')) {
      // If there is an active section, push it.
      if (currentSection.heading || currentSection.content) {
        result.push({ heading: currentSection.heading, content: currentSection.content.trim() });
      }
      // Start new section with heading (remove the colon)
      currentSection = { heading: trimmed.slice(0, -1), content: '' };
    } else {
      // Check if the line contains a colon (e.g. "Thought: I now know the final answer")
      const colonIndex = trimmed.indexOf(':');
      if (colonIndex > 0) {
        // If the part before the colon appears to be a heading (e.g. "Thought"), then treat it as a new section.
        const potentialHeading = trimmed.slice(0, colonIndex).trim();
        const potentialContent = trimmed.slice(colonIndex + 1).trim();
        // If currentSection is not empty, push it.
        if (currentSection.heading || currentSection.content) {
          result.push({ heading: currentSection.heading, content: currentSection.content.trim() });
        }
        currentSection = { heading: potentialHeading, content: potentialContent + ' ' };
      } else {
        // Otherwise, add the line to the current section's content.
        currentSection.content += trimmed + ' ';
      }
    }
  }
  if (currentSection.heading || currentSection.content) {
    result.push({ heading: currentSection.heading, content: currentSection.content.trim() });
  }
  return result;
}
// PROPS
const props = defineProps({
  
  userId: {
    type: String,
    default: ''
  },
  conversationId: {
    type: String,
    default: ''
  },
  runId: {
    type: String,
    default: ''
  },
  agentData: {
    type: Array,
    default: () => []
  },
  metadata: {
    type: Object, // or Array, depending on your data
    default: () => ({}) // or [] if you expect an array
  }
})
const agentThoughtsData = ref([])
const metadata = ref(null)


watch(
  () => props.metadata,
  (newMetadata, oldMetadata) => {
    // console.log('Child saw array change from', newAgentData, 'to', oldAgentData)
    console.log(
      'Child sawold Metadata array change from',
      ((oldMetadata)),
      'to',
      (((newMetadata)))
    );
    // console.log(typeof newMetadata)
    
    metadata.value = ((newMetadata)) || null
    
  

  },
  { deep: true } // If you want to detect nested mutations
)
watch(
  () => props.agentData,
  (newAgentData, oldAgentData) => {
    // console.log('Child saw array change from', newAgentData, 'to', oldAgentData)
    console.log(
      'Child saw array change from',
      ((oldAgentData)),
      'to',
      (((newAgentData)))
    );
    console.log(typeof newAgentData)
    

      agentThoughtsData.value = ((newAgentData)) || []    

  },
  { deep: true } // If you want to detect nested mutations
)
const collapsed = ref(false)

// SSE
const messages = ref([])
let eventSource = null
let firstMessageArrived = false
let lastFinalAnswer = '' // for deduping repeated final answers

// Refs
const scrollContainer = ref(null)

// ICONS
const icons = {
  thought: `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 8a3 3 0 00-6 0v1a3 3 0 00-3 3v1.17
               a2 2 0 01-.586 1.414l-1 1
               a1 1 0 001.414 1.414L7 16.414
               A2 2 0 008.414 17H15
               a3 3 0 003-3v-1a3 3 0 00-3-3V8z"/>
    </svg>
  `,
  action: `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"/>
    </svg>
  `,
  actionInput: `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 20h9m-9-4h9m-9-4h9M3 4h1
               a2 2 0 012 2v12a2 2 0 01-2 2H3
               a2 2 0 01-2-2V6a2 2 0 012-2z"/>
    </svg>
  `,
  observation: `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M5 3c-1.1 0-2 .9-2 2v13
               a2 2 0 002 2h14
               a2 2 0 002-2V5
               a2 2 0 00-2-2H5zm2 10l3 3l7-7"/>
    </svg>
  `,
  finalAnswer: `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4"
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 9l-7 7-4-4"/>
    </svg>
  `
}

// Agent color mapping
const agentStyleMap = {
  'Aggregator Search Agent': { backgroundColor: '#F3E8FF' },
  'Data Extraction Agent': { backgroundColor: '#E7F9F1' },
  'Market Trends Analyst': { backgroundColor: '#FFFBEA' },
  'Outreach Specialist': { backgroundColor: '#E7F3FF' }
}

function getAgentStyle(agentName) {
  const style = agentStyleMap[agentName]
  if (style) {
    return { 'background-color': style.backgroundColor }
  }
  return { 'background-color': '#F1F5F9' }
}
function getAgentIcon(agentName) {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600"
         fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 4v16m8-8H4"/>
    </svg>
  `
}

/**
 * parseMessage => splits text into segments: Thought, Action, etc.
 * Also handles truncation for "observation" segments.
 */


/**
 * SSE connect
 */
/**
 * Actually scroll to bottom of the container
 */
function autoScrollToBottom() {
  if (!scrollContainer.value) return
  // nextTick => setTimeout => do scroll
  nextTick(() => {
    setTimeout(() => {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }, 50)
  })
}

/**
 * Watch messages => autoScroll #2 (in case SSE immediate wasn't enough)
 */
watch(messages, () => {
  autoScrollToBottom()
})

// Lifecycle
onMounted(() => {
  // connectToSSE()
  // connectWebSocket()


})

onBeforeUnmount(() => {
 
})

// watch runId => if changes => reset + reconnect
// watch(() => props.runId, (newVal, oldVal) => {
//   if (newVal && newVal !== oldVal) {
//     messages.value = []
//     lastFinalAnswer = ''
//     firstMessageArrived = false
//     collapsed.value = false
//     connectToSSE()
//   }
// })

// watch userId => reset + reconnect
// watch(() => props.userId, (newVal, oldVal) => {
//   if (newVal && newVal !== oldVal) {
//     messages.value = []
//     lastFinalAnswer = ''
//     firstMessageArrived = false
//     connectToSSE()
//   }
// })



function parsedData(str) {
  try {
    return JSON.parse(str)
  } catch (err) {
    return str // or an error object
  }
}


const presentMetadata = computed(() => {
  const data = [];

  if (props.metadata.total_tokens != null) {
    data.push({
      key: 'total_tokens',
      label: 'Total tokens:',
      value: props.metadata.total_tokens
    });
  }
  if (props.metadata.prompt_tokens != null) {
    data.push({
      key: 'prompt_tokens',
      label: 'Prompt tokens:',
      value: props.metadata.prompt_tokens
    });
  }
  if (props.metadata.cached_prompt_tokens != null) {
    data.push({
      key: 'cached_prompt_tokens',
      label: 'Cached prompt tokens:',
      value: props.metadata.cached_prompt_tokens
    });
  }
  if (props.metadata.completion_tokens != null) {
    data.push({
      key: 'completion_tokens',
      label: 'Completion tokens:',
      value: props.metadata.completion_tokens
    });
  }
  if (props.metadata.successful_requests != null) {
    data.push({
      key: 'successful_requests',
      label: 'Successful requests:',
      value: props.metadata.successful_requests
    });
  }
  if (props.metadata.duration != null) {
    data.push({
      key: 'duration',
      label: 'total Duration',
      value: `${props.metadata.duration}s`
    });
  }
  return data;
});


const formattedDuration=(duration) =>{
      // Format duration to 2 decimal places
      return duration?.toFixed(2);
    }
</script>

<style scoped>
/* The container is "h-screen", ensuring the messages can scroll within "flex-1 overflow-y-auto". */
</style>
