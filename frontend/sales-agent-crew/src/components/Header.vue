<template>
  <header class="bg-blue-50 shadow-md">
    <div class="h-16 mx-auto px-6 flex items-center justify-between">
      <!-- Left: Logo & Brand -->
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-2 shadow-md">
          <span class="text-2xl text-white">🔍</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">
          Sales Sphere
        </h1>
      </div>

      <!-- Right: DateTime -->
      <div class="text-sm text-gray-600">
        {{ currentDateTime }}
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const currentDateTime = computed(() => {
const now = new Date()
return new Intl.DateTimeFormat('en-US', {
  dateStyle: 'full',
  timeStyle: 'medium'
}).format(now)
})
</script>