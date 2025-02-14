<template>
    <!-- Timeline Item -->
    <div :class="['group relative flex', collapsed ? 'min-h-16' : '']">
      <!-- Icon Container (always visible; timeline line is part of this container) -->
      <div :class="iconContainerClasses">
        <div class="relative z-10 size-6 flex justify-center items-center" v-html="iconSvg"></div>
      </div>
      <!-- End Icon -->
  
      <!-- Right Content -->
      <div class="grow pb-2 group-last:pb-0">
        <!-- Always show period -->
        <h3 class="mb-1 text-lg text-gray-600 dark:text-neutral-400">
          {{ parsedData?.event }}
        </h3>
        <!-- Only show the rest if not collapsed -->
        <template v-if="!collapsed">
          <div 
            @click="isOpen = !isOpen"  
            class="flex justify-between items-center cursor-pointer min-w-0"
          >
            <div class="flex items-center flex-1 min-w-0">
              <CorrectIcon class="mr-1 flex-shrink-0" />
              <span class="truncate text-brandTextSecondary font-semibold text-sm">
                <!-- {{ title }} -->
                {{ parsedData?.event }}
              </span>
            </div>
            <!-- Arrow icon toggles direction based on accordion state -->
            <div class="transition-all duration-300 flex-shrink-0">
              <svg
                v-if="!isOpen"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600 transform rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div v-show="isOpen">
            <p v-if="description" class="mt-1 text-sm text-gray-600 dark:text-neutral-400">
              <!-- {{ description }} -->
            </p>
            <ul v-if="bullets?.length" class="list-disc ms-6 mt-3 space-y-1.5">
              <li
                v-for="(bullet, index) in bullets"
                :key="index"
                class="ps-1 text-sm text-gray-600 dark:text-neutral-400"
              >
                <!-- {{ bullet }} -->
              </li>
            </ul>
            <!-- Optional Card Section -->
            <div v-if="card" class="mt-3 hidden">
              <a
                :href="card.href"
                class="block border border-gray-200 rounded-lg hover:shadow-sm focus:outline-none dark:border-neutral-700"
              >
                <div class="relative flex items-center overflow-hidden">
                  <img
                    :src="card.imgSrc"
                    :alt="card.imgAlt"
                    class="w-full absolute inset-0 object-cover rounded-s-lg"
                  />
                  <div class="grow p-4 ms-32 sm:ms-48">
                    <div class="min-h-24 flex flex-col justify-center">
                      <h3 class="font-semibold text-sm text-gray-800 dark:text-neutral-300">
                        <!-- {{ card.title }} -->
                      </h3>
                      <p class="mt-1 text-sm text-gray-500 dark:text-neutral-500">
                        <!-- {{ card.subtitle }} -->
                      </p>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </template>
        <template v-if="!collapsed">
          <div 
            @click="isOpen = !isOpen"  
            class="flex justify-between mt-2 items-center cursor-pointer min-w-0"
          >
            <div class="flex items-center flex-1 min-w-0">
              <CorrectIcon class="mr-1 flex-shrink-0" />
              <span class="truncate text-brandTextSecondary font-semibold text-sm">
                <!-- {{ title }} -->
              </span>
            </div>
            <!-- Arrow icon toggles direction based on accordion state -->
            <div class="transition-all duration-300 flex-shrink-0">
              <svg
                v-if="!isOpen"
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 text-gray-600 transform rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          <div v-show="isOpen">
            <p v-if="description" class="mt-1 text-sm text-gray-600 dark:text-neutral-400">
              <!-- {{ description }} -->
            </p>
            <ul v-if="bullets?.length" class="list-disc ms-6 mt-3 space-y-1.5">
              <li
                v-for="(bullet, index) in bullets"
                :key="index"
                class="ps-1 text-sm text-gray-600 dark:text-neutral-400"
              >
                <!-- {{ bullet }} -->
              </li>
            </ul>
            <!-- Optional Card Section -->
            <div v-if="card" class="mt-3 hidden">
              <a
                :href="card.href"
                class="block border border-gray-200 rounded-lg hover:shadow-sm focus:outline-none dark:border-neutral-700"
              >
                <div class="relative flex items-center overflow-hidden">
                  <img
                    :src="card.imgSrc"
                    :alt="card.imgAlt"
                    class="w-full absolute inset-0 object-cover rounded-s-lg"
                  />
                  <div class="grow p-4 ms-32 sm:ms-48">
                    <div class="min-h-24 flex flex-col justify-center">
                      <h3 class="font-semibold text-sm text-gray-800 dark:text-neutral-300">
                        <!-- {{ card.title }} -->
                      </h3>
                      <p class="mt-1 text-sm text-gray-500 dark:text-neutral-500">
                        <!-- {{ card.subtitle }} -->
                      </p>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </template>
      </div>
      <!-- End Right Content -->
    </div>
  </template>
  
  <script setup>
  import { computed, ref } from 'vue'
  import CorrectIcon from '@/components/icons/CorrectIcon.vue'
  


  // The parent passes a JSON string as the "data" prop.
  const props = defineProps({
    data: {
      type: [],
      required: true
    }
  });
  
  const parsedData = computed(() => {
  try {
    return (props.data)
  } catch (error) {
    console.error('Error parsing data in ChatBubble:', error)
    return {}
  }
});


  



// // 2. Choose which sub-component to display based on agent_type
// const selectedComponent = computed(() => {
//   switch (parsedData.value.agent_type) {
//     case 'assistant':
//       return AssistantComponent
//     case 'user_proxy':
//       return UserProxyComponent
//     // Add cases for other agent types as needed
//     default:
//       return UnknownTypeComponent
//   }
// });
  const isOpen = ref(false);

  
  // Compute the classes for the icon container.
  // This remains unchanged so that the timeline line is always visible.
  const iconContainerClasses = computed(() => {
    let base =
      "relative after:absolute after:top-8 after:bottom-2 after:start-3 after:w-px after:-translate-x-[0.5px] after:bg-gray-200 dark:after:bg-neutral-700"
    if (props.isLast) {
      base += " after:hidden"
    }
    return base
  })
  </script>
  
  <style scoped>
  /* You can adjust min-h-16 (4rem) to a different value if needed */
  </style>
  