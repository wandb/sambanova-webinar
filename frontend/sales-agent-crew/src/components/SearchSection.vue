<template>
  <div class="bg-white rounded-xl shadow-md border border-gray-100 p-6">
    <div class="flex items-center space-x-4">
      <div class="relative flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Example: Generate leads for retail startups in California interested in AI"
          class="block w-full pl-5 pr-12 py-4 text-base rounded-lg border border-gray-300 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200"
          @keyup.enter="handleSearch"
          :disabled="isLoading || isRecording"
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
        @click="handleSearch"
        :disabled="isLoading || isRecording"
        class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-medium rounded-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50"
      >
        {{ isLoading ? 'Searching...' : 'Search' }}
      </button>
    </div>
    
    <!-- Recording Status -->
    <div v-if="isRecording" class="mt-2 text-sm text-gray-600 flex items-center space-x-2">
      <span class="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
      <span>Recording... Click microphone to stop</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@clerk/vue'
import { decryptKey } from '../utils/encryption' // Import the decryptKey function

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['search'])
const searchQuery = ref('')
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const { userId } = useAuth()
const sambanovaKey = ref(null)

// Load API key on mount and decrypt it
onMounted(async () => {
  try {
    const encryptedKey = localStorage.getItem(`sambanova_key_${userId}`)
    if (encryptedKey) {
      sambanovaKey.value = await decryptKey(encryptedKey)
    } else {
      sambanovaKey.value = null
    }
  } catch (error) {
    console.error('Failed to load API key:', error)
  }
})

const handleSearch = () => {
  if (!searchQuery.value.trim()) return
  emit('search', searchQuery.value)
}

const toggleRecording = async () => {
  if (isRecording.value) {
    console.log('Stopping recording...');
    stopRecording();
  } else {
    console.log('Starting recording...');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      startRecording(stream);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check your permissions.');
    }
  }
};

const startRecording = (stream) => {
  console.log('MediaRecorder started');

  audioChunks.value = [];

  const options = { mimeType: 'audio/webm' }; // Change if necessary
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
    console.warn(`${options.mimeType} is not supported, using default MIME type.`);
    delete options.mimeType;
  }

  mediaRecorder.value = new MediaRecorder(stream, options);

  mediaRecorder.value.ondataavailable = (event) => {
    console.log('Data available:', event.data.size);
    if (event.data.size > 0) {
      audioChunks.value.push(event.data);
    }
  };

  mediaRecorder.value.onstop = async () => {
    console.log('Recording stopped');
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' });
    console.log('Audio blob size:', audioBlob.size);

    await transcribeAudio(audioBlob);

    // Stop all tracks
    stream.getTracks().forEach((track) => track.stop());
  };

  mediaRecorder.value.start();
  isRecording.value = true;
};

const stopRecording = () => {
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop()
    isRecording.value = false
  }
}

const transcribeAudio = async (audioBlob) => {
  console.log('Transcribing audio...');

  try {
    if (!sambanovaKey.value) {
      throw new Error('SambaNova API key is missing. Please add it in the settings.');
    }

    const audioArrayBuffer = await audioBlob.arrayBuffer();
    console.log('Audio blob size:', audioBlob.size);

    // Convert the audio data to Base64
    const audioBase64 = btoa(
      new Uint8Array(audioArrayBuffer)
        .reduce((data, byte) => data + String.fromCharCode(byte), '')
    );

    // Construct the request body
    const requestBody = {
      model: 'Qwen2-Audio-7B-Instruct', // Replace with the actual model name
      messages: [
        {
          role: 'system',
          content: 'You are an Automatic Speech Recognition tool.',
        },
        {
          role: 'user',
          content: [
            {
              type: 'audio_content',
              audio_content: {
                content: `data:audio/webm;base64,${audioBase64}`,
              },
            },
          ],
        },
        {
          role: 'user',
          content: 'Please transcribe the previous audio and only return the transcription.',
        },
      ],
      response_format: 'streaming',
      stream: true,
    };

    // Make the API request
    const response = await fetch('https://api.sambanova.ai/v1/audio/reasoning', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${sambanovaKey.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', response.status, errorText);
      alert(`Transcription failed with status ${response.status}: ${errorText}`);
      throw new Error(`Transcription failed: ${errorText}`);
    }

    // Handle the streaming response
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
          
          if (dataStr === '[DONE]') {
            // Stream finished
            break
          }

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

    // Clean the transcription
    const cleanedText = cleanTranscription(transcribedText);

    // Update search query and trigger search
    searchQuery.value = cleanedText.trim()
    if (searchQuery.value) {
      handleSearch()
    }

  } catch (error) {
    console.error('Transcription error:', error)
    alert(error.message || 'Failed to transcribe audio. Please try again.')
  }
}

// Function to clean the transcription
function cleanTranscription(transcribedText) {
  // Define possible prefixes
  const prefixes = [
    "The transcription of the audio is:",
    "The transcription is:",
  ];

  // Trim whitespace
  let cleanedText = transcribedText.trim();

  // Check for each prefix
  for (const prefix of prefixes) {
    if (cleanedText.startsWith(prefix)) {
      // Remove prefix
      cleanedText = cleanedText.slice(prefix.length).trim();
      break;
    }
  }

  // Remove surrounding quotes if present
  if (
    (cleanedText.startsWith("'") && cleanedText.endsWith("'")) ||
    (cleanedText.startsWith('"') && cleanedText.endsWith('"'))
  ) {
    cleanedText = cleanedText.slice(1, -1).trim();
  }

  return cleanedText;
}
</script>