import { createRouter, createWebHistory } from 'vue-router'
import Tap from './pages/Tap.vue'
import Wifi from './pages/Wifi.vue'
import Register from './pages/Register.vue'
import PayResult from './pages/PayResult.vue'
import Dashboard from './pages/store/Dashboard.vue'
import Ledger from './pages/admin/Ledger.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Tap },
    { path: '/wifi', component: Wifi },
    { path: '/register', component: Register },
    { path: '/pay-result', component: PayResult },
    { path: '/store/dashboard', component: Dashboard },
    { path: '/admin/ledger', component: Ledger }
  ]
})
