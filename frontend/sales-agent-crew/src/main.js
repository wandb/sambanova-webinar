// main.js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { clerkPlugin } from '@clerk/vue'

// Import your router
import router from './router/index.js'

const PUBLISHABLE_KEY = 'pk_test_dHJ1c3RlZC1sb2JzdGVyLTgwLmNsZXJrLmFjY291bnRzLmRldiQ'

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing Publishable Key')
}

// Create and mount the app
const app = createApp(App)
app.use(clerkPlugin, { publishableKey: PUBLISHABLE_KEY })
app.use(router)
app.mount('#app')
