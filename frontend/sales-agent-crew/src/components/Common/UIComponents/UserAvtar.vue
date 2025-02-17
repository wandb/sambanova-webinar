<template>
    <span :class="avatarClass">
      <span class="text-sm font-medium text-white leading-none">
          {{ getInitials(user.firstName, user.lastName) }}
      </span>
    </span>
  </template>
  
<script setup>
import { computed } from 'vue'

import { useUser } from '@clerk/vue'
const { user, isLoaded, isSignedIn } = useUser()

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



function getInitials(firstName, lastName) {
  let initials = '';
  if (firstName && typeof firstName === 'string' && firstName.trim().length > 0) {
    initials += firstName.trim().charAt(0).toUpperCase();
  }
  if (lastName && typeof lastName === 'string' && lastName.trim().length > 0) {
    initials += lastName.trim().charAt(0).toUpperCase();
  }
  return initials;
}
</script>
<style scoped>
/* Scoped CSS if any additional styling is needed */


</style>
