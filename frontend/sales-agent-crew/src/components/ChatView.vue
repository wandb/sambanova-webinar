<!-- src/components/chat/ChatView.vue -->
<template>
    <div class="flex flex-col h-full">
      <!-- If no conversation selected, show placeholder -->
      <div v-if="!conversationId" class="flex-1 flex items-center justify-center text-gray-400">
        <p>No conversation selected. Create or pick one in the sidebar.</p>
      </div>
  
      <div v-else class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx"
          :class="msg.role === 'user' ? 'text-right' : 'text-left'"
          class="my-1"
        >
          <div 
            :class="[
              'inline-block px-3 py-2 rounded-lg text-sm',
              msg.role === 'user'
                ? 'bg-primary-100 text-gray-800'
                : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>
      </div>
  
      <!-- Input box at bottom -->
      <div class="p-4 border-t border-gray-200">
        <form @submit.prevent="sendMessage" class="flex space-x-2">
          <input
            v-model="draftMessage"
            type="text"
            class="flex-1 border border-gray-300 rounded-md p-2"
            placeholder="Type your message..."
          />
          <button
            type="submit"
            class="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            :disabled="!conversationId"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch, onMounted, nextTick } from 'vue'
  import axios from 'axios'
  
  const props = defineProps({
    conversationId: {
      type: String,
      default: ''
    },
    userId: {
      type: String,
      default: 'anonymous'
    }
  })
  
  const messages = ref([])
  const draftMessage = ref('')
  const messagesContainer = ref(null)
  
  /**
   * When conversationId changes, we fetch the entire conversation 
   * from /newsletter_chat/history/{conversationId}
   */
  watch(() => props.conversationId, async (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      messages.value = []
      await loadFullHistory()
    }
  })
  
  onMounted(async () => {
    if (props.conversationId) {
      await loadFullHistory()
    }
  })
  
  async function loadFullHistory() {
    if (!props.conversationId) return
    try {
      const resp = await axios.get(`${import.meta.env.VITE_API_URL}/newsletter_chat/history/${props.conversationId}`, {
        headers: {
          'x-user-id': props.userId
        }
      })
      const data = resp.data
      if (Array.isArray(data.messages)) {
        messages.value = data.messages
      } else {
        messages.value = []
      }
      await nextTick()
      scrollToBottom()
    } catch (err) {
      console.error('Error loading conversation history:', err)
      messages.value = []
    }
  }
  
  async function sendMessage() {
    const txt = draftMessage.value.trim()
    if (!txt || !props.conversationId) return
    messages.value.push({ role: 'user', content: txt })
    draftMessage.value = ''
  
    await nextTick()
    scrollToBottom()
  
    try {
      const resp = await axios.post(`${import.meta.env.VITE_API_URL}/newsletter_chat/message/${props.conversationId}`, {
        message: txt
      }, {
        headers: {
          'x-user-id': props.userId
        }
      })
      const assistantReply = resp.data.assistant_response
      messages.value.push({ role: 'assistant', content: assistantReply })
  
      await nextTick()
      scrollToBottom()
    } catch (err) {
      console.error('Error sending message:', err)
      messages.value.push({
        role: 'assistant',
        content: 'Error: Could not process your message.'
      })
    }
  }
  
  function scrollToBottom() {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
  </script>
  