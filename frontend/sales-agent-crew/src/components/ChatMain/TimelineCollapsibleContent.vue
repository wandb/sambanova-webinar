<template>
  <div class="mx-2 mb-2" @click="isOpen = !isOpen">
    <div class="flex justify-between items-center cursor-pointer">
      <div class="flex items-start flex-1 no-wrap">
        <CorrectIcon class="mr-1 flex-shrink-0" />
        <!-- If heading is non-numeric, display formatted key -->
        <span v-if="!isNumeric(heading)" class="text-primary-brandTextSecondary text-sm">
          {{ formatKey(heading) }}:
        </span>
        <!-- If heading is numeric and value has a name property, display that -->
        <span v-else-if="isNumeric(heading) && value.name" class="text-primary-brandTextSecondary text-sm">
          {{ value.name ? value.name : value.search }}
        </span>
        <!-- Otherwise if heading is numeric, display fallback (e.g. search_query) -->
        <span v-else-if="isNumeric(heading)" class="text-primary-brandTextSecondary text-sm">
          {{ value?.search_query }}
        </span>
      </div>
      <!-- Arrow icon toggles direction based on accordion state -->
      <div class="transition-all duration-300 flex-shrink-0">
        <svg v-if="!isOpen"
             xmlns="http://www.w3.org/2000/svg"
             class="h-4 w-4 text-[#667085]"
             fill="none"
             viewBox="0 0 24 24"
             stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 9l-7 7-7-7" />
        </svg>
        <svg v-else
             xmlns="http://www.w3.org/2000/svg"
             class="h-4 w-4 text-[#667085] transform rotate-180"
             fill="none"
             viewBox="0 0 24 24"
             stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
    <div class="m-1 p-1 border rounded-md bg-primary-brandGray" v-show="isOpen">
      <!-- If value is an object that looks like a schema -->
      <div v-if="isObject(value) && !Array.isArray(value) && hasSchema(value)">
        <table class="w-full border divide-y divide-gray-200">
          <tbody class="divide-y divide-gray-200">
            <tr>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">Type:</td>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">{{ value.type }}</td>
            </tr>
            <tr>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">Description:</td>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">{{ value.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- If value is a plain object (non-schema) -->
      <div v-else-if="isObject(value) && !Array.isArray(value)">
        <table class="w-full border divide-y divide-gray-200">
          <tbody class="divide-y divide-gray-200">
            <tr v-for="(val, key) in value" :key="key">
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">
                {{ formatKey(key) }}
              </td>
              <td class="px-1 py-2 whitespace-nowrap text-xs text-gray-900">
                <RecursiveDisplay :value="val" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- If value is an array, render as a bullet list -->
      <div v-else-if="Array.isArray(value)">
        <ul class="list-disc ml-6 space-y-1">
          <li v-for="(item, index) in value" :key="index">
            <RecursiveDisplay :value="item" />
          </li>
        </ul>
      </div>

      <!-- If heading is numeric and value has a description -->
      <div v-else-if="isNumeric(heading) && value?.description">
        {{ value.description }}
      </div>

      <!-- Otherwise, render as plain text -->
      <div v-else>
        <p class="text-sm">{{ value }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CorrectIcon from '@/components/icons/CorrectIcon.vue'
import RecursiveDisplay from './RecursiveDisplay.vue'

// Local state for accordion toggle.
const isOpen = ref(false);

// Define props.
const props = defineProps({
  heading: {
    type: String,
    required: true
  },
  value: {
    type: null,
    required: true
  }
});

// Checks if a value is numeric.
function isNumeric(val) {
  return !isNaN(Number(val));
}

// Checks if a value is an object.
function isObject(val) {
  return val !== null && typeof val === 'object';
}

// Check if the object appears to be a schema (has both "type" and "description").
function hasSchema(obj) {
  return obj && Object.prototype.hasOwnProperty.call(obj, 'type') && Object.prototype.hasOwnProperty.call(obj, 'description');
}

// Format a key: replace underscores with spaces and capitalize each word.
function formatKey(key) {
  key = String(key);
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
</script>

<style scoped>
/* Adjust styles as needed */
</style>
