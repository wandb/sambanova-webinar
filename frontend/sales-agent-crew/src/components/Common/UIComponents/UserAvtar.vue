<script setup>
import { computed } from 'vue'

import { useUser } from '@clerk/vue'

const props = defineProps({
  initials: {
    type: String,
    default: 'AD', // Default initials if none are provided
  },
  bgColor: {
    type: String,
    default: 'bg-gray-600', // Default background color
  }
})

const avatarClass = computed(() => `shrink-0 inline-flex items-center justify-center size-[38px] rounded-md ${props.bgColor}`)
</script>

<template>
  <span :class="avatarClass">
    <span class="text-sm font-medium text-white leading-none">
      AD
    </span>
  </span>
</template>
<script setup>

</script>
<style scoped>
/* Scoped CSS if any additional styling is needed */


</style>
