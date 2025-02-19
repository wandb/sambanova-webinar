<template>
    <div>
      <!-- If value is an object (but not an array), render a table -->
      <div v-if="isObject(value) && !Array.isArray(value)">
        <table 
        :class="isRecursive?'':' '"
        class="table-auto w-full border-0 ">
          <tbody class="bg-white ">
            <tr v-for="(val, key) in value" :key="key">
              <td class="px-4 py-2 w-[40px] text-xs text-gray-900 capitalize break-words">
                {{ key }}
              </td>
              <td class="px-4 py-2 text-xs text-gray-900 break-words">
                <!-- Recursively display each nested value -->
                <RecursiveDisplay :isRecursive="true" :value="val" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- If value is an array, render as a bullet list -->
      <div v-else-if="Array.isArray(value)">
        <ul :class="!isRecursive?'':'list-disc'" class=" ml-6 space-y-1">
          <li v-for="(item, index) in value" :key="index">
            <RecursiveDisplay :isRecursive="true" :value="item" />
          </li>
        </ul>
      </div>
  
      <!-- Otherwise, render as plain text -->
      <div v-else>
        <p class="text-xs break-words">{{ value }}</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, isReactive } from 'vue'
  import RecursiveDisplay from './RecursiveDisplay.vue'
  
  const props = defineProps({
    value: {
      type: null,
      required: true
    },
    isRecursive: {
      type: null,
      required: true
    },

  })
  
  function isObject(val) {

    

    return val !== null && typeof (val) === 'object'
  }
  </script>
  
  <style scoped>
  table {
    table-layout: auto;
  }
  </style>
  