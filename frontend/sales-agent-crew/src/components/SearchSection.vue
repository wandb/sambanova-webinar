<template>
  <div class="bg-white rounded-xl shadow-md border border-gray-100 p-6">
    <!-- Warning Message for missing keys -->
    <div v-if="missingKeys.length > 0" class="mb-4 p-4 rounded-lg bg-yellow-50 border border-yellow-200">
      <div class="flex">
        <svg class="h-6 w-6 text-yellow-600 flex-shrink-0 mr-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
        <div>
          <p class="text-yellow-700">
            Please set up your {{ missingKeys.join(', ') }} API key{{ missingKeys.length > 1 ? 's' : '' }} in the
            <button 
              @click="openSettings"
              class="text-yellow-800 underline hover:text-yellow-900 font-medium"
            >
              settings
            </button>
          </p>
        </div>
      </div>
    </div>

    <!-- Search Input Area -->
    <div class="flex items-center space-x-4">
      <div class="relative flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter your search query..."
          class="w-full p-3 pr-12 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          :disabled="isLoading"
        />

        <!-- Voice Input Button -->
        <button
          @click="toggleRecording"
          :disabled="isLoading"
          :class="{
            'text-orange-500': !isRecording,
            'text-red-500 animate-pulse': isRecording
          }"
          class="absolute right-4 top-1/2 transform -translate-y-1/2 p-2 hover:bg-gray-100 rounded-full transition-colors"
          title="Voice Search"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            class="h-6 w-6" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" 
            />
          </svg>
        </button>
      </div>

      <button
        @click="performSearch"
        :disabled="isLoading || !searchQuery.trim()"
        class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
      >
        <span v-if="!isLoading">Search</span>
        <span v-else>Searching...</span>
      </button>
    </div>

    <!-- Recording Status -->
    <div v-if="isRecording" class="mt-2 text-sm text-gray-600 flex items-center space-x-2">
      <span class="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
      <span>Recording... Click microphone to stop</span>
    </div>

    <!-- Error Modal -->
    <ErrorModal
      :show="showErrorModal"
      :errorMessage="errorMessage"
      @close="showErrorModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuth } from '@clerk/vue'
import { decryptKey } from '../utils/encryption'
import ErrorModal from './ErrorModal.vue'
import axios from 'axios'

const props = defineProps({
  keysUpdated: {
    type: Number,
    default: 0,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  // The runId from MainLayout
  runId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['searchStart', 'searchComplete', 'searchError', 'openSettings'])

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
          // Make sure to pass runId here if your backend expects it for "route" 
          // (But typically only needed on "execute"... optional)
          'x-user-id': userId.value || '',
          'x-run-id': props.runId || ''
        }
      }
    )

    const detectedType = routeResp.data.type
   
    // 3) Tell parent "searchStart" with final type
    emit('searchStart', detectedType || 'unknown')

    // 4) Execute the final query
    const executeResp = await axios.post(
      `${import.meta.env.VITE_API_URL}/execute/${detectedType}`,
      routeResp.data.parameters,
      {
        headers: {
          'Content-Type': 'application/json',
          'x-sambanova-key': sambanovaKey.value || '',
          'x-serper-key': serperKey.value || '',
          'x-exa-key': exaKey.value || '',
          // **Crucial**: same user/run ID as SSE 
          'x-user-id': userId.value || '',
          'x-run-id': props.runId || ''
        }
      }
    )

    // 5) searchComplete
    emit('searchComplete', {
      type: detectedType,
      query: searchQuery.value,
      results: executeResp.data
    })

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

function openSettings() {
  emit('openSettings')
}
</script>

<style scoped>
/* Basic styling for demonstration. */
</style>
