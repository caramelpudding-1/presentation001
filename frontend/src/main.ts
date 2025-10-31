import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
  })
}

createApp(App).use(router).mount('#app')
