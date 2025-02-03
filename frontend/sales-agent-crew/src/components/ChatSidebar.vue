<!-- src/components/chat/ChatSidebar.vue -->
<template>
    <div class="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      <!-- Header -->
      <div class="px-4 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="font-semibold text-gray-900">Conversations</h2>
        <button
          class="p-2 bg-primary-100 text-primary-700 rounded hover:bg-primary-200 text-sm"
          @click="createNewChat"
        >
          + New
        </button>
      </div>
  
      <!-- Conversation list -->
      <div class="flex-1 overflow-y-auto">
        <div 
          v-for="conv in conversations" 
          :key="conv.conversation_id"
          class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
          @click="selectConversation(conv)"
        >
          <div class="font-medium text-gray-800 truncate">
            {{ conv.title }}
          </div>
          <div class="text-xs text-gray-500">
            {{ formatDateTime(conv.created_at) }}
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  /**
   * We'll store in localStorage under key "my_conversations_<userId>" 
   * an array of { conversation_id, title, created_at (ms) }
   */
  
  const emit = defineEmits(['selectConversation'])
  
  const userId = ref('testuser123') // or from your Clerk user
  const conversations = ref([])
  
  /** 
   * On mount, load from localStorage
   */
  function loadConversations() {
    try {
      const dataStr = localStorage.getItem(`my_conversations_${userId.value}`)
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
    localStorage.setItem(`my_conversations_${userId.value}`, JSON.stringify(conversations.value))
  }
  
  onMounted(() => {
    loadConversations()
  })
  
  async function createNewChat() {
    try {
      // In a real app, fetch user keys from local storage or your store
      const sambanovaKey = localStorage.getItem('sambanova_key') || ''
      const serperKey = localStorage.getItem('serper_key') || ''
      const exaKey = localStorage.getItem('exa_key') || ''
  
      const resp = await axios.post(`${import.meta.env.VITE_API_URL}/newsletter_chat/init`, {}, {
        headers: {
          'x-sambanova-key': sambanovaKey,
          'x-serper-key': serperKey,
          'x-exa-key': exaKey,
          'x-user-id': userId.value
        }
      })
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
    } catch (err) {
      console.error('Error creating new chat:', err)
      alert('Failed to create new conversation.')
    }
  }
  
  function selectConversation(conv) {
    emit('selectConversation', conv)
  }
  
  function formatDateTime(ts) {
    if (!ts) return ''
    const d = new Date(ts)
    return d.toLocaleString()
  }
  </script>
  