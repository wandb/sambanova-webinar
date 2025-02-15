<!-- src/components/chat/ChatView.vue -->
<template>
  <div class="relative h-full w-full">
<!-- Content -->
<div class="relative h-full">
  <div class="py-10 lg:py-14 h-full">
    <!-- Title -->
    <div class="max-w-4xl px-4 sm:px-6 lg:px-8 mx-auto text-center">
      <a class="inline-block mb-4 flex-none focus:outline-none focus:opacity-80" href="/" aria-label="SI Agent">
       
       <SILogo/>
      </a>

      <h1  class="text-3xl font-bold text-gray-800 sm:text-4xl dark:text-white">
        Welcome to SI Agents
      </h1>
      <p class="mt-3 text-gray-600 dark:text-neutral-400">
        Your AI-powered agent
      </p>
    </div>
    <!-- End Title -->
<!-- 
    <div v-for="msgItem in messagesData" 
        :key="msgItem.conversation_id"
        class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100">
        <div class="font-medium text-gray-800 truncate">
         Message  {{ msgItem.event	 }}
        </div>
        <div class="text-xs text-gray-500">
          {{msgItem.data }}
        </div>
      </div> -->
    <ul class="mt-16 space-y-5">
      <!-- Chat Bubble -->
     
         <!-- {{msgItem.event}}  {{msgItem.data}}        -->
        <ChatBubble v-for="msgItem in messagesData" 
        :key="msgItem.conversation_id" :event="msgItem.event" :data="msgItem.data"  />
      
      
      <!-- End Chat Bubble -->

     
      <!-- End Chat Bubble -->
    </ul>
  </div>
<div class="sticky bottom-0 left-0 right-0 bg-white  p-2">
  <div class="sticky bottom-0 z-10  border-t border-gray-200 pt-2 pb-3 sm:pt-4 sm:pb-6 dark:bg-neutral-900 dark:border-neutral-700">
    <!-- Textarea -->

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-0">
      <div class="flex justify-between items-center mb-3">
        <button type="button" class="inline-flex justify-center items-center gap-x-2 rounded-lg font-medium text-gray-800 hover:text-blue-600 focus:outline-none focus:text-blue-600 text-xs sm:text-sm dark:text-neutral-200 dark:hover:text-blue-500 dark:focus:text-blue-500">
          <svg class="shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          New chat
        </button>
      <StatusText  v-if="isLoading"/>
        <button type="button" class="py-1.5 px-2 inline-flex items-center gap-x-2 text-xs font-medium rounded-lg border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-white dark:hover:bg-neutral-800 dark:focus:bg-neutral-800">
          <svg class="size-3" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5z"/>
          </svg>
          Stop generating
        </button>
      </div>

      <!-- Input -->
      <div class="relative">
        <textarea 
        v-model="searchQuery"
          type="search"
          placeholder="Ask me about...companies to target, research topics, or company stocks and financials"   
          :disabled="isLoading"
        class="p-4 pb-12 block w-full  bg-gray-100 border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:outline-none active:outline-none border  focus:border-orange-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-neutral-900 dark:border-neutral-700 dark:text-neutral-400 dark:placeholder-neutral-500 dark:focus:ring-neutral-600"
        
         ></textarea>

        <!-- Toolbar -->
       
        <div class="absolute bottom-px inset-x-px p-2 rounded-b-lg bg-gray-100">
        <div class="flex justify-between items-center">
          <!-- Button Group -->
          <div class="flex items-center">
            <!-- Mic Button -->
            <button
           
              class="inline-flex hidden shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-1 focus:outline-none focus:bg-gray-100"
            >
              <svg
              
                class="shrink-0 size-4"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <line x1="9" x2="15" y1="15" y2="9" />
              </svg>

             
  

            </button>
            
            <!-- End Mic Button -->
            <!-- Attach Button -->
            <button
              @click="$refs.fileInput.click()"
          :disabled="isLoading"
              type="button"
              class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-1 focus:outline-none focus:bg-gray-100"
            >
              <svg
                class="shrink-0 size-4"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            </button>
            <!-- End Attach Button -->
          </div>
          <!-- End Button Group -->
          <!-- Button Group -->
          <div class="flex items-center gap-x-1">
            <!-- Mic Button -->
            <Popover text="Use voice mode" position="top" color="bg-black text-white">

            <button
            type="button"
              @click="toggleRecording"
          :disabled="isLoading"
          :class="{
            'text-gray-500': !isRecording,
            'text-orange-500 ': isRecording
          }"
              

              class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-gray-500 hover:bg-gray-100 focus:z-1 focus:outline-none focus:bg-gray-100"
            >
            <svg 
               v-if="!isRecording"
            className="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
      <path fill-rule="evenodd" d="M5 8a1 1 0 0 1 1 1v3a4.006 4.006 0 0 0 4 4h4a4.006 4.006 0 0 0 4-4V9a1 1 0 1 1 2 0v3.001A6.006 6.006 0 0 1 14.001 18H13v2h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-2H9.999A6.006 6.006 0 0 1 4 12.001V9a1 1 0 0 1 1-1Z" clip-rule="evenodd"/>
      <path d="M7 6a4 4 0 0 1 4-4h2a4 4 0 0 1 4 4v5a4 4 0 0 1-4 4h-2a4 4 0 0 1-4-4V6Z"/>
    </svg>
             
              <svg  v-else className="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
  <path d="M7 5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H7Z"/>
</svg>
              
      
            </button>
            </Popover>
            <!-- End Mic Button -->
            <!-- Send Button -->
            <button
              type="button"
              @click="addMessage"
        :disabled="isLoading || !searchQuery.trim()"
        
              class="inline-flex shrink-0 justify-center items-center size-8 rounded-lg text-white bg-orange-600 hover:bg-orange-500 focus:z-1 disabled:opacity-50 focus:outline-none focus:bg-orange-500"
            >
              <svg
                class="shrink-0 size-3.5"
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
              >
                <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083l6-15Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z" />
              </svg>
            </button>
            <!-- End Send Button -->
          </div>
          <!-- End Button Group -->
        </div>
      </div>
        <!-- End Toolbar -->
      </div>
      <!-- End Input -->
    </div>
    <!-- End Textarea -->
  </div>
</div>
</div>
<!-- End Content -->
 
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick,onBeforeUnmount ,computed} from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { useRoute, useRouter } from 'vue-router'
import SILogo from '@/components/icons/SILogo.vue' 
import axios from 'axios'
import ChatBubble from '@/components/ChatMain/ChatBubble.vue'
const router = useRouter()
const route = useRoute() 
import { useAuth } from '@clerk/vue'
import { decryptKey } from '../../utils/encryption'
import ErrorModal from '../ErrorModal.vue'
import { uploadDocument } from '../../services/api'
import Popover from '@/components/Common/UIComponents/CustomPopover.vue'
import StatusText from '@/components/Common/StatusText.vue'
import { DocumentArrowUpIcon, XMarkIcon } from '@heroicons/vue/24/outline'
const newMessage = ref('') // User input field
const socket = ref(null) // WebSocket reference


const emit = defineEmits(['searchStart', 'searchComplete', 'searchError', 'openSettings',"agentThoughtsDataChanged"])
const props = defineProps({
  conversationId: {
    type: String,
    default: ''
  },
  userId: {
    type: String,
    default: 'anonymous'
  },
  keysUpdated: {
    type: Number,
    default: 0,
  },
  
  // The runId from MainLayout
  runId: {
    type: String,
    default: ''
  },
  sessionId: {
    type: String,
    default: ''
  }
})

const messages = ref([])
const draftMessage = ref('')
const assistantThinking = ref(false)
const isLoading = ref(false)
const messagesContainer = ref(null)

// Observe conversation changes => reload
// watch(() => props.conversationId, async (newVal, oldVal) => {
//   if (newVal && newVal !== oldVal) {
//     messages.value = []
//     await loadFullHistory()
//   }
// })

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId) {
      messagesData.value=[]
      currentId.value = newId
      loadPreviousChat(newId)
       // Close the existing WebSocket connection if it exists.
       if (socket.value) {
        socket.value.close()
      }
        // Create a new WebSocket connection with the updated currentId.
        connectWebSocket()
    }
  }
)

// On mount => load if we have conversation
// onMounted(async () => {
//   // if (props.conversationId) {
//   //   await loadFullHistory()
//   // }


  
// })

async function loadFullHistory() {
  if (!props.conversationId) return
  try {
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/newsletter_chat/history/${props.conversationId}`,
      {
        headers: { 'x-user-id': props.userId }
      }
    )
    const data = resp.data
    if (Array.isArray(data.messages)) {
      messages.value = data.messages.map(parseMessage)
    } else {
      messages.value = []
    }
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('[ChatView] Error loading conversation history:', err)
    messages.value = []
  }
}
let userIdStatic="user_2sfDzHK9r5FkXrufqoAFjnjGNPk"
let convIdStatic="db5ff51c-2886-46f6-bbda-6f041ad69a41"
async function loadPreviousChat(convId) {
  try {

    isLoading.value=true
    // if (missingKeys.value.length > 0) {
    //   alert(`Missing required keys: ${missingKeys.value.join(', ')}`)
    //   return
    // }

    // const uid = userId.value || 'anonymous'
    const resp = await axios.get(
      `${import.meta.env.VITE_API_URL}/chat/history/${userId.value}/${convId}`, 
      {}, 
      
    )
    isLoading.value=false

      console.log(resp)
      filterChat((resp.data))
  } catch (err) {
    console.error('Error creating new chat:', err)
    alert('Failed to create new conversation. Check keys or console.')
  }
}

// Reactive variable to store the ID
const currentId = ref(route.params.id || '')


const messagesData = ref([])
const agentThoughtsData = ref([])

 const filterChat=async (msgData)=>{

  messagesData.value=msgData.messages.filter(message => message.event === "completion"||message.event === "user_message")
  // agentThoughtsData.value=msgData.messages.filter(message => message.event === "think");
  agentThoughtsData.value = msgData.messages
  .filter(message => message.event === "think")
  .reduce((acc, message) => {
    try {
      const parsed = JSON.parse(message.data);
      acc.push(parsed);
    } catch (error) {
      console.error("Failed to parse JSON for message:", message, error);
    }
    return acc;
  }, []);

  emit('agentThoughtsDataChanged', agentThoughtsData.value)
  await nextTick()


}

// Marked config => GFM, line breaks, highlight
function renderMarkdown(content) {
  marked.setOptions({
    gfm: true,
    breaks: true,
    smartypants: true,
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value
      }
      return hljs.highlightAuto(code).value
    }
  })
  return marked(content || '')
}

function parseMessage(msg) {
  return {
    ...msg,
    typing: false,
    formattedContent: renderMarkdown(msg.content)
  }
}

// Submit user message => call API => push assistant reply
async function sendMessage() {
  const txt = draftMessage.value.trim()
  if (!txt || !props.conversationId) return

  const userMsg = {
    role: 'user',
    content: txt,
    typing: false,
    formattedContent: renderMarkdown(txt)
  }
  messages.value.push(userMsg)
  draftMessage.value = ''
  assistantThinking.value = true
  await nextTick()
  scrollToBottom()

  try {
    const resp = await axios.post(
      `${import.meta.env.VITE_API_URL}/newsletter_chat/message/${props.conversationId}`,
      { message: txt },
      {
        headers: { 'x-user-id': props.userId }
      }
    )
    const assistantReply = resp.data.assistant_response || ''
    const assistantMsg = {
      role: 'assistant',
      content: assistantReply,
      typing: false,
      formattedContent: renderMarkdown(assistantReply)
    }
    messages.value.push(assistantMsg)
  } catch (err) {
    console.error('[ChatView] Error sending message:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Error: Could not process your message.',
      typing: false,
      formattedContent: 'Error: Could not process your message.'
    })
  } finally {
    assistantThinking.value = false
    await nextTick()
    scrollToBottom()
  }
}

// Scroll after rendering
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}







// Reactive state
const searchQuery = ref('')
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const sambanovaKey = ref(null)
const exaKey = ref(null)
const serperKey = ref(null)
const errorMessage = ref('')
const showErrorModal = ref(false)
const fileInput = ref(null)
const uploadStatus = ref(null)

// Add new reactive state for documents
const uploadedDocuments = ref([])
const selectedDocuments = ref([])

// Clerk
const { userId } = useAuth()

async function loadKeys() {
  try {
    const encryptedSambanovaKey = localStorage.getItem(`sambanova_key_${userId.value}`)
    const encryptedExaKey = localStorage.getItem(`exa_key_${userId.value}`)
    const encryptedSerperKey = localStorage.getItem(`serper_key_${userId.value}`)

    if (encryptedSambanovaKey) {
      sambanovaKey.value = await decryptKey(encryptedSambanovaKey)
    } else {
      sambanovaKey.value = null
    }

    if (encryptedExaKey) {
      exaKey.value = await decryptKey(encryptedExaKey)
    } else {
      exaKey.value = null
    }

    if (encryptedSerperKey) {
      serperKey.value = await decryptKey(encryptedSerperKey)
    } else {
      serperKey.value = null
    }
  } catch (error) {
    console.error('Error loading keys:', error)
    errorMessage.value = 'Error loading API keys'
    showErrorModal.value = true
  }
}

onMounted(async () => {
  await loadKeys()
  await loadUserDocuments()
  authRequest()
  // connectWebSocket()
})

watch(
  () => props.keysUpdated,
  async () => {
    await loadKeys()
  },
  { immediate: true }
)

const missingKeys = computed(() => {
  const missing = []
  if (!sambanovaKey.value) missing.push('SambaNova')
  if (!exaKey.value) missing.push('Exa')
  if (!serperKey.value) missing.push('Serper')
  return missing
})

async function performSearch() {
  try {
    // 1) Indicate we are about to do "routing_query"
    emit('searchStart', 'routing_query')

    // 2) Determine route
    const routeResp = await axios.post(
      `${import.meta.env.VITE_API_URL}/route`,
      { query: searchQuery.value },
      {
        headers: {
          'Content-Type': 'application/json',
          'x-sambanova-key': sambanovaKey.value || '',
          'x-user-id': userId.value || '',
          'x-run-id': props.runId || ''
        }
      }
    )

    const detectedType = routeResp.data.type
   
    // 3) Tell parent "searchStart" with final type
    emit('searchStart', detectedType || 'unknown')

    // 4) Execute the final query with selected documents
    const parameters = {
      ...routeResp.data.parameters,
      document_ids: selectedDocuments.value
    }

    const executeResp = await axios.post(
      `${import.meta.env.VITE_API_URL}/execute/${detectedType}`,
      parameters,
      {
        headers: {
          'Content-Type': 'application/json',
          'x-sambanova-key': sambanovaKey.value || '',
          'x-serper-key': serperKey.value || '',
          'x-exa-key': exaKey.value || '',
          'x-user-id': userId.value || '',
          'x-run-id': props.runId || '',
          'x-session-id': props.sessionId || ''
        }
      }
    )

    // 5) searchComplete
    emit('searchComplete', {
      type: detectedType,
      query: searchQuery.value,
      results: executeResp.data
    })

    // 6) Clear search query
    searchQuery.value = ''

  } catch (error) {
    console.error('[SearchSection] performSearch error:', error)
    emit('searchError', error)
  }
}

/**
 * Voice recording / transcription (unchanged)
 */
function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecordingFlow()
  }
}

async function startRecordingFlow() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    startRecording(stream)
  } catch (error) {
    console.error('Error accessing microphone:', error)
    alert('Unable to access microphone. Please check your permissions.')
  }
}

function startRecording(stream) {
  audioChunks.value = []
  const options = { mimeType: 'audio/webm' }
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
    console.warn(`${options.mimeType} is not supported, using default MIME type.`)
    delete options.mimeType
  }

  mediaRecorder.value = new MediaRecorder(stream, options)

  mediaRecorder.value.ondataavailable = (event) => {
    if (event.data.size > 0) {
      audioChunks.value.push(event.data)
    }
  }

  mediaRecorder.value.onstop = async () => {
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
    await transcribeAudio(audioBlob)
    stream.getTracks().forEach((track) => track.stop())
  }

  mediaRecorder.value.start()
  isRecording.value = true
}

function stopRecording() {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
    isRecording.value = false
  }
}

async function transcribeAudio(audioBlob) {
  try {
    if (!sambanovaKey.value) {
      throw new Error('SambaNova API key is missing. Please add it in the settings.')
    }

    const audioArrayBuffer = await audioBlob.arrayBuffer()
    const audioBase64 = btoa(
      new Uint8Array(audioArrayBuffer)
        .reduce((data, byte) => data + String.fromCharCode(byte), '')
    )

    const requestBody = {
      model: 'Qwen2-Audio-7B-Instruct',
      messages: [
        {
          role: 'system',
          content: 'You are an Automatic Speech Recognition tool.'
        },
        {
          role: 'user',
          content: [
            {
              type: 'audio_content',
              audio_content: {
                content: `data:audio/webm;base64,${audioBase64}`
              },
            },
          ]
        },
        {
          role: 'user',
          content: 'Please transcribe the previous audio and only return the transcription.'
        },
      ],
      response_format: 'streaming',
      stream: true,
    }

    const response = await fetch('https://api.sambanova.ai/v1/audio/reasoning', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${sambanovaKey.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('API Error:', response.status, errorText)
      alert(`Transcription failed with status ${response.status}: ${errorText}`)
      throw new Error(`Transcription failed: ${errorText}`)
    }

    // streaming response
    const streamReader = response.body.getReader()
    let transcribedText = ''
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await streamReader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n').filter(line => line.trim())

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim()
          if (dataStr === '[DONE]') break
          try {
            const data = JSON.parse(dataStr)
            if (data.choices?.[0]?.delta?.content) {
              transcribedText += data.choices[0].delta.content
            }
          } catch (e) {
            console.error('Error parsing JSON:', e, 'Data string:', dataStr)
          }
        }
      }
    }

    const cleanedText = cleanTranscription(transcribedText)
    searchQuery.value = cleanedText.trim()

    if (searchQuery.value) {
      performSearch()
    }

  } catch (error) {
    console.error('Transcription error:', error)
    alert(error.message || 'Failed to transcribe audio. Please try again.')
  }
}

function cleanTranscription(transcribedText) {
  let cleanedText = transcribedText.trim()
  const prefixes = [
    'The transcription of the audio is:',
    'The transcription is:',
  ]
  for (const prefix of prefixes) {
    if (cleanedText.startsWith(prefix)) {
      cleanedText = cleanedText.slice(prefix.length).trim()
      break
    }
  }
  // Remove surrounding quotes if present
  if (
    (cleanedText.startsWith("'") && cleanedText.endsWith("'")) ||
    (cleanedText.startsWith('"') && cleanedText.endsWith('"'))
  ) {
    cleanedText = cleanedText.slice(1, -1).trim()
  }
  return cleanedText
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    uploadStatus.value = { type: 'info', message: 'Uploading document...' }
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/upload`,
      formData,
      {
        headers: {
          'x-user-id': userId.value || '',
        }
      }
    )
    // Store the uploaded document
    const document = response.data.document
    uploadedDocuments.value.push(document)
    selectedDocuments.value.push(document.id)
    uploadStatus.value = { type: 'success', message: 'Document uploaded successfully!' }
    
    // Clear the file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (error) {
    console.error('[SearchSection] Upload error:', error)
    uploadStatus.value = { 
      type: 'error', 
      message: error.response?.data?.error || 'Failed to upload document' 
    }
  }
}



// Load user's documents on mount
async function loadUserDocuments() {
  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/documents/${userId.value}`
    )
    uploadedDocuments.value = response.data.documents
  } catch (error) {
    console.error('[SearchSection] Error loading documents:', error)
  }
}
function toggleDocumentSelection(docId) {
  const index = selectedDocuments.value.indexOf(docId)
  if (index === -1) {
    selectedDocuments.value.push(docId)
  } else {
    selectedDocuments.value.splice(index, 1)
  }
}
async function authRequest() {
  
  // const baseUrl = import.meta.env.VITE_API_URL || ''
  const url = `http://localhost:8000/set_api_keys/${props.userId}` // Replace with your API URL
  const postParams = {
    "sambanova_key": "8f462f72-0a98-42cc-a5ca-e784470cb85f",
  "serper_key": "fa053a785d306bc110c0dd657d220b1825338f67",
  "exa_key": "f2f5b5bf-84da-472f-8711-088dfbe9e04c"
  }

  try {
    const response = await axios.post(url, postParams)
    if (response.status === 200) {
      // Call the next function after success
    
      // connectWebSocket()
    }
  } catch (error) {
    console.error('Error in POST request:', error)
  }
}

onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close()
  }
})

const addMessage=()=>{
   isLoading.value=true

  try{  
  if (!searchQuery.value.trim()) return

const messagePayload = {
  event: "user_message",
  data: searchQuery.value,
  timestamp: new Date().toISOString()
}

// Add message to local state so the user sees it immediately
messagesData.value.push(messagePayload)

// Send message via WebSocket
socket.value.send(JSON.stringify(messagePayload))

// Clear input field
searchQuery.value = ''
// isLoading.value=false

}catch(e){
    console.log("ChatView error", e)
  }
}



// Function to establish the WebSocket connection.
function connectWebSocket() {


  const WEBSOCKET_URL = 'ws://localhost:8000/chat'
  const fullUrl = `${WEBSOCKET_URL}?user_id=${userId.value}&conversation_id=${currentId.value}`

  socket.value = new WebSocket(fullUrl)

  socket.value.onopen = () => {
    console.log('WebSocket connection opened')
  }

  socket.value.onmessage = (event) => {
    try {
      const receivedData = JSON.parse(event.data)

      // Add new message to messages array
      
      if(receivedData.event=="user_message"||receivedData.event=="completion"){

        messagesData.value.push(receivedData)
        isLoading.value=false
        
      }

    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  socket.value.onclose = () => {
    console.log('WebSocket closed, attempting to reconnect...')
    setTimeout(connectWebSocket, 5000) // Auto-reconnect after 5 seconds
  }


}
async function removeDocument(docId) {
  try {
    // Remove from backend
    await axios.delete(
      `${import.meta.env.VITE_API_URL}/documents/${userId.value}/${docId}`
    )
    // Remove from selected documents if it was selected
    const selectedIndex = selectedDocuments.value.indexOf(docId)
    if (selectedIndex !== -1) {
      selectedDocuments.value.splice(selectedIndex, 1)
    }
    // Remove from uploaded documents list
    uploadedDocuments.value = uploadedDocuments.value.filter(doc => doc.id !== docId)
    // Show success message
    uploadStatus.value = { type: 'success', message: 'Document removed successfully!' }
    setTimeout(() => {
      uploadStatus.value = null
    }, 3000)
  } catch (error) {
    console.error('[SearchSection] Error removing document:', error)
    uploadStatus.value = { 
      type: 'error', 
      message: error.response?.data?.error || 'Failed to remove document' 
    }
  }
}
</script>

<style scoped>
/* Loader animation for 'typing' placeholder */
.loader-dots {
  width: 15px;
  height: 3px;
  position: relative;
}
.loader-dots::before,
.loader-dots::after,
.loader-dots > div {
  content: '';
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #9ca3af;
  position: absolute;
  animation: loader-dots 0.8s infinite ease-in-out;
}
.loader-dots::before {
  left: 0;
}
.loader-dots > div {
  left: 6px;
}
.loader-dots::after {
  left: 12px;
}
@keyframes loader-dots {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Syntax highlighting background, code block style */
.hljs {
  background: #f9fafb;
  padding: 0.5em;
  border-radius: 4px;
  overflow-x: auto;
}

/* For <h1>, <h2>, <h3> etc. plus paragraphs, lists, etc. using tailwind typography */
.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}
.prose p {
  margin: 0.5rem 0;
}
.prose ul, .prose ol {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}
.prose li {
  margin: 0.25rem 0;
}

.hljs-keyword {
  color: #7c3aed;
  font-weight: bold;
}
.hljs-string {
  color: #15803d;
}
</style>
