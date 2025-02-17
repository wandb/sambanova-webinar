<template>
  <div class="flex-container">
    <h1 class="box-progress" :data-text="text">{{ text }}</h1>
    <!-- <span class="box-text">{{ number }}%</span> -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted ,toRefs} from 'vue'


// Declare the prop using defineProps
const props = defineProps({
  text: {
    type: String,
    default: 'Loading...'
  }
})

// You can destructure it for ease of use:
const { text } = toRefs(props)

const number = ref(0)

onMounted(() => {
  const interval = setInterval(() => {
    number.value += 1
  }, 10000)

  onUnmounted(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
.flex-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-family: "Titillium Web", sans-serif;
}

.box-text {
  color: rgba(31, 41, 55, 0.8);
}

.box-progress {
  color: rgba(31, 41, 55, 0.3);
  position: relative;
}

.box-progress:before {
  content: attr(data-text);
  position: absolute;
  overflow: hidden;
  max-width: 6.5em;
  white-space: nowrap;
  color: orange;
  animation: loading 2s linear infinite;
}

@keyframes loading {
  0% {
    max-width: 0;
  }
  100% {
    max-width: 100%;
  }
}
</style>
