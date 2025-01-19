<template>
  <header class="shadow-md bg-white">
    <div class="h-16 mx-auto px-6 flex items-center justify-between">
      <!-- Left: Logo & Brand -->
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <img 
            src="https://sambanova.ai/hubfs/sambanova-logo-black.png" 
            alt="Samba Sales Co-Pilot Logo" 
            class="h-8"
          />
        </div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">
          Samba Sales Co-Pilot
        </h1>
      </div>

      <!-- Right: User Button and DateTime -->
      <div class="flex items-center space-x-6">
        <div class="text-sm text-gray-600">
          {{ currentDateTime }}
        </div>
        <SignedIn>
          <UserButton 
            afterSignOutUrl="/login" 
            :appearance="{ elements: { avatarBox: 'h-10 w-10' } }"
          />
        </SignedIn>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { SignedIn, UserButton } from '@clerk/vue'

const currentDateTime = computed(() => {
  const now = new Date()
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'full',
    timeStyle: 'medium'
  }).format(now)
})
</script>