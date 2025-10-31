<template>
  <div class="card">
    <h2>かんたん登録</h2>
    <div class="grid">
      <label>E-mail
        <input class="input" type="email" v-model="email" placeholder="you@example.com">
      </label>
      <label>Wallet（任意）
        <input class="input" type="text" v-model="wallet" placeholder="0x...">
      </label>
      <div class="grid cols2">
        <button class="btn" @click="back">戻る</button>
        <button class="btn primary" @click="submit" :disabled="loading">登録</button>
      </div>
    </div>
    <div v-if="msg" style="margin-top:.8rem; color:#86efac;">{{ msg }}</div>
    <div v-if="error" style="margin-top:.8rem; color:#fca5a5;">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { api } from '@/api'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const session_id = Number(route.query.session_id)

const email = ref('')
const wallet = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const msg = ref<string | null>(null)

function back(){ router.back() }

async function submit(){
  try {
    loading.value = true
    await api.register(session_id, email.value || undefined, wallet.value || undefined)
    msg.value = '登録しました。体験を続けられます。'
    setTimeout(() => router.push({ path:'/wifi', query:{ session_id }}), 600)
  } catch(e:any) {
    error.value = e?.message
  } finally {
    loading.value = false
  }
}
</script>
