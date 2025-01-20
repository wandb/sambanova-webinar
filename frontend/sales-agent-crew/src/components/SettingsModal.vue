<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex min-h-screen items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black opacity-30" @click="close"></div>

      <!-- Modal -->
      <div class="relative w-full max-w-2xl bg-white rounded-xl shadow-lg p-6">
        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {{ errorMessage }}
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-4 p-3 bg-green-100 text-green-700 rounded">
          {{ successMessage }}
        </div>

        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">API Settings</h2>
          <button @click="close" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-6">
          <!-- SambaNova API Key -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              SambaNova API Key
              <a 
                href="https://cloud.sambanova.ai/"
                target="_blank"
                class="text-primary-600 hover:text-primary-700 ml-2"
              >
                Get Key →
              </a>
            </label>
            <input
              type="password"
              v-model="sambanovaKey"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="Enter your SambaNova API key"
            />
          </div>

          <!-- Exa API Key -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Exa API Key
              <a 
                href="https://dashboard.exa.ai/login?redirect=/"
                target="_blank"
                class="text-primary-600 hover:text-primary-700 ml-2"
              >
                Get Key →
              </a>
            </label>
            <input
              type="password"
              v-model="exaKey"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="Enter your Exa API key"
            />
          </div>

          <div class="flex justify-end space-x-4 mt-6">
            <button
              @click="close"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              @click="saveKeys"
              class="px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700"
              :disabled="isSaving"
            >
              {{ isSaving ? 'Saving...' : 'Save Keys' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@clerk/vue'
import { encryptKey, decryptKey } from '../utils/encryption'

const isOpen = ref(false)
const sambanovaKey = ref('')
const exaKey = ref('')
const isSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const { userId } = useAuth()

// Load keys on mount
onMounted(async () => {
  await loadKeys()
})

const loadKeys = async () => {
  try {
    const savedSambanovaKey = localStorage.getItem(`sambanova_key_${userId}`)
    const savedExaKey = localStorage.getItem(`exa_key_${userId}`)
    
    if (savedSambanovaKey) {
      sambanovaKey.value = await decryptKey(savedSambanovaKey)
    }
    if (savedExaKey) {
      exaKey.value = await decryptKey(savedExaKey)
    }
  } catch (error) {
    console.error('Failed to load keys:', error)
    errorMessage.value = 'Failed to load saved keys'
  }
}

const saveKeys = async () => {
  isSaving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    if (!sambanovaKey.value || !exaKey.value) {
      throw new Error('Both API keys are required')
    }

    const encryptedSambanovaKey = await encryptKey(sambanovaKey.value)
    const encryptedExaKey = await encryptKey(exaKey.value)
    
    localStorage.setItem(`sambanova_key_${userId}`, encryptedSambanovaKey)
    localStorage.setItem(`exa_key_${userId}`, encryptedExaKey)
    
    successMessage.value = 'Keys saved successfully!'
    setTimeout(() => {
      close()
    }, 1500)
  } catch (error) {
    console.error('Failed to save keys:', error)
    errorMessage.value = error.message || 'Failed to save keys. Please try again.'
  } finally {
    isSaving.value = false
  }
}

const close = () => {
  isOpen.value = false
  errorMessage.value = ''
  successMessage.value = ''
}

// Explicitly define what we're exposing
defineExpose({
  isOpen,
  getKeys: async () => {
    try {
      const savedSambanovaKey = localStorage.getItem(`sambanova_key_${userId}`)
      const savedExaKey = localStorage.getItem(`exa_key_${userId}`)
      
      if (!savedSambanovaKey || !savedExaKey) {
        return null
      }

      return {
        sambanovaKey: await decryptKey(savedSambanovaKey),
        exaKey: await decryptKey(savedExaKey)
      }
    } catch (error) {
      console.error('Failed to retrieve keys:', error)
      return null
    }
  }
})
</script> 