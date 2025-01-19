<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <img 
          src="https://sambanova.ai/hubfs/sambanova-logo-black.png" 
          alt="SambaNova Logo" 
          class="h-12 mx-auto mb-6"
        />
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Sales Co-Pilot</h1>
        <p class="text-lg text-gray-600">AI-Powered Sales Intelligence</p>
      </div>
      
      <div class="bg-white rounded-xl shadow-lg p-8">
        <SignIn 
          :appearance="{ 
            elements: {
              headerTitle: 'hidden',
              headerSubtitle: 'hidden',
              footerAction: 'hidden'
            }
          }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { SignIn } from '@clerk/vue'
</script>