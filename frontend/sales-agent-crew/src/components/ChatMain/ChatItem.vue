<template>
    <div
      class="p-3   m-1 relative cursor-pointer  group"
      @click="onSelectConversation"
      :class="{ 'bg-primary-brandDarkGray rounded-md border border border-primary-brandFrame': isActive }"
    >
      <!-- Menu button: visible on hover -->
      <button
        type="button"
        class="absolute right-1 top-1 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        @click.stop="toggleMenu"
        @mousedown.stop
        aria-label="Open menu"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="5" r="1" />
          <circle cx="12" cy="12" r="1" />
          <circle cx="12" cy="19" r="1" />
        </svg>
      </button>
  
      <!-- Popover menu -->
      <div
        v-if="activeMenu"
        class="absolute right-1 top-8 bg-white border border-gray-200 shadow-lg rounded z-30"
        @click.stop
      >
        <button
          class="flex items-center w-full px-4 py-2 hover:bg-gray-100 text-left"
          @click="onDelete"
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6l-1 14H6L5 6" />
            <path d="M10 11v6" />
            <path d="M14 11v6" />
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
          </svg>
          Delete
        </button>
        <button
          class="flex items-center w-full px-4 py-2 hover:bg-gray-100 text-left"
          @click="onShare"
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7" />
            <polyline points="12 3 12 12" />
            <polyline points="9 6 12 3 15 6" />
          </svg>
          Share
        </button>
        <button
          class="flex items-center w-full px-4 py-2 hover:bg-gray-100 text-left"
          @click="onDownload"
        >
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="#667085" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download
        </button>
      </div>
  
      <!-- Conversation details -->
      <div class="w-full relative h-full">
        <div
          class="font-medium capitalize text-gray-800 truncate"
          
        >
          {{ conversation.name ? conversation.name : "New Chat" }}
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ChatItem',
    props: {
      conversation: {
        type: Object,
        required: true,
      },
      preselectedChat: {
        type: [String, Number],
        default: null,
      },
    },
    data() {
      return {
        activeMenu: false,
      };
    },
    computed: {
      isActive() {
        return this.preselectedChat === this.conversation.conversation_id;
      },
    },
    methods: {
      onSelectConversation() {
        this.$emit('select-conversation', this.conversation);
        // Optionally, close the menu when the conversation is selected.
        this.activeMenu = false;
      },
      toggleMenu() {
        this.activeMenu = !this.activeMenu;
      },
      onDelete() {
        this.$emit('delete-chat', this.conversation.conversation_id);
        this.activeMenu = false;
      },
      onShare() {
        this.$emit('share-chat', this.conversation.conversation_id);
        this.activeMenu = false;
      },
      onDownload() {
        this.$emit('download-chat', this.conversation.conversation_id);
        this.activeMenu = false;
      },
    },
  };
  </script>
  
  <style scoped>
  /* Additional styles (if needed) */
  </style>
  