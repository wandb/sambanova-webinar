<!-- src/components/chat/ChatSidebar.vue -->
<template>
  <div class="w-64 h-full  border border-primary-brandFrame bg-white rounded-lg bg-white  flex flex-col">
    <!-- Header -->
    <div class="px-4 py-4 border-b border-gray-200 flex items-center justify-between">
      
      <button
        class="p-2 border w-full border-primary-brandBorder text-primary-brandColor rounded  text-sm"
        @click="createNewChat"
        :disabled="missingKeys.length > 0"
      >
        + New Chat
      </button>
    </div>

    <!-- If missing any key, show a small alert -->
    <div v-if="missingKeys.length > 0" class="bg-yellow-50 text-yellow-700 text-sm p-2">
      Missing {{ missingKeys.join(', ') }} key(s). Please set them in settings.
    </div>

    <!-- Conversation list -->
    <div class="flex-1 overflow-y-auto">
      <div 
        v-for="conv in conversations" 
        :key="conv.conversation_id"
        class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100">
      <div @click="selectConversation(conv)" class="w-full">
        <div class="font-medium text-gray-800 truncate">  
          {{ conv.name	 }}
          
        </div>
        <div class="text-xs text-gray-500">
          {{ conv.conversation_id }}
        </div>
        <div class="text-xs text-gray-500">
          {{ formatDateTime(conv.created_at) }}
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

import { useAuth } from '@clerk/vue'
import { decryptKey } from '@/utils/encryption'   // adapt path if needed
import { useRoute, useRouter } from 'vue-router'
import SILogo from '@/components/icons/SILogo.vue'  


import axios from 'axios'
const router = useRouter()
const route = useRoute() 
/**
 * We'll store in localStorage under key "my_conversations_<userId>"
 * an array of { conversation_id, title, created_at }
 */
const emit = defineEmits(['selectConversation'])

/** Clerk user */
const { userId } = useAuth()

const sambanovaKey = ref(null)
const serperKey = ref(null)
const exaKey = ref(null)

const conversations = ref([])

/** 
 * On mounted => load local conversation list + decrypt keys 
 */
onMounted(() => {
  // loadConversations()
  loadChats()
  loadKeys()
  // connectWebSocket()
})
let convId="db5ff51c-2886-46f6-bbda-6f041ad69a41"
let userIdStatic="user_2sfDzHK9r5FkXrufqoAFjnjGNPk"
async function loadKeys() {
  try {
    const uid = userId.value || 'anonymous'
    const encryptedSamba = localStorage.getItem(`sambanova_key_${uid}`)
    const encryptedSerp = localStorage.getItem(`serper_key_${uid}`)
    const encryptedExa = localStorage.getItem(`exa_key_${uid}`)

    sambanovaKey.value = encryptedSamba ? await decryptKey(encryptedSamba) : null
    serperKey.value     = encryptedSerp ? await decryptKey(encryptedSerp) : null
    exaKey.value        = encryptedExa  ? await decryptKey(encryptedExa)  : null
  } catch (err) {
    console.error('[ChatSidebar] Error decrypting keys:', err)
  }
}

const missingKeys = computed(() => {
  const missing = []
  if (!sambanovaKey.value) missing.push('SambaNova')
  if (!serperKey.value) missing.push('Serper')
  if (!exaKey.value) missing.push('Exa')
  return missing
})


async function loadChats() {
  try {
    
    // if (missingKeys.value.length > 0) {
    //   alert(`Missing required keys: ${missingKeys.value.join(', ')}`)
    //   return
    // }

    const uid = userId.value || 'anonymous'
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/chat/list/user_2sfDzHK9r5FkXrufqoAFjnjGNPk`,   
    )
   
   console.log(resp)

   conversations.value = resp.data?.chats;

  } catch (err) {
    console.error('Error creating new chat:', err)
    alert('Failed to create new conversation. Check keys or console.')
  }
}

function loadConversations() {
  try {
    const uid = userId.value || 'anonymous'
    const dataStr = localStorage.getItem(`my_conversations_${uid}`)
    if (!dataStr) {
      conversations.value = []
      return
    }
    conversations.value = JSON.parse(dataStr)
  } catch {
    conversations.value = []
  }
}

function saveConversations() {
  const uid = userId.value || 'anonymous'
  localStorage.setItem(`my_conversations_${uid}`, JSON.stringify(conversations.value))
}

/** Start a new conversation => calls /newsletter_chat/init with decrypted keys */
async function createNewChat() {
  try {
    if (missingKeys.value.length > 0) {
      alert(`Missing required keys: ${missingKeys.value.join(', ')}`)
      return
    }

    const uid = userId.value || 'anonymous'
    const resp = await axios.post(
      `${import.meta.env.VITE_API_URL}/chat/init`, 
      {}, 
      {
        headers: {
          'x-sambanova-key': sambanovaKey.value || '',
          'x-serper-key': serperKey.value || '',
          'x-exa-key': exaKey.value || '',
          'x-user-id': uid
        }
      }
    )
    const cid = resp.data.conversation_id
    const assistantMsg = resp.data.assistant_message || "New Conversation"
    const shortTitle = assistantMsg.substring(0, 30).replace(/\n/g,' ').trim() || "New Chat"

    const convMeta = {
      conversation_id: cid,
      title: shortTitle,
      created_at: Date.now()
    }
    // Prepend
    conversations.value.unshift(convMeta)
    saveConversations()

    selectConversation(convMeta)
    router.push(`/${cid}`)
  } catch (err) {
    console.error('Error creating new chat:', err)
    alert('Failed to create new conversation. Check keys or console.')
  }
}
async function loadOldConversations() {
  try {
    if (missingKeys.value.length > 0) {
      alert(`Missing required keys: ${missingKeys.value.join(', ')}`)
      return
    }

    const uid = userId.value || 'anonymous'
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/chat/history/${userIdStatic}/${convId}`, 
      {}, 
      
    )
    console.log(resp)
    
  } catch (err) {
    console.error('Error creating new chat:', err)
    alert('Failed to create new conversation. Check keys or console.')
  }
}



/** Emit an event so parent can handle "selectConversation" */
function selectConversation(conv) {
  emit('selectConversation', conv)

  alert(conv.conversation_id)
  router.push(`/${conv.conversation_id}`)

}

function formatDateTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleString()
}

const addMessage=()=>{

  let myMessage="analyse microsoft financial reports this quarter"
  const payload = {
      event: "user_input",
      data: myMessage,
      id: Date.now(),
    }
    socket.send(JSON.stringify(payload))
}

let socket = null

// Function to establish the WebSocket connection.
function connectWebSocket() {

  
  const WEBSOCKET_URL = 'ws://localhost:8000/chat'  // Replace with your actual URL
  // Construct the full URL using query parameters.
  const fullUrl = `${WEBSOCKET_URL}?user_id=${userIdStatic}&conversation_id=${convId}`
  console.log('Connecting to:', fullUrl)
  // alert("connectng ",fullUrl)
  socket = new WebSocket(fullUrl)

  socket.onopen = () => {
    console.log('WebSocket connection opened')
    // Log the connection open event.
    // logs.value += `Connection opened at ${new Date().toLocaleTimeString()}\n`
    // Send the initial payload.
    // const payload = {
    //   event: "user_input",
    //   data: "Iphone vs android"
    // }
    // socket.send(JSON.stringify(payload))
    // logs.value += `Sent: ${JSON.stringify(payload)}\n`

  }

  socket.onmessage = (event) => {
    console.log('Received message:', event.data)
    // Append the received data to the log with a newline.
    // logs.value += `${event.data}\n`

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
    // logs.value += `Error: ${error.message || 'Unknown error'}\n`
  }

  socket.onclose = (event) => {
    console.log('WebSocket connection closed:', event)
    // logs.value += `Connection closed at ${new Date().toLocaleTimeString()}\n`
  }
}
</script>
