<template>
  <div class="card">
    <h2>接続中 …</h2>
    <p>FREE時間のあいだ体験できます。一定時間後に登録のご案内が出ます。</p>

    <FreeTimer :usedMinutes="used" :freeRemaining="freeRemaining" />

    <div class="grid cols2">
      <button class="btn" @click="beat" :disabled="loading">Heartbeat 送信</button>
      <button class="btn primary" @click="finish" :disabled="loading">Finish & Settle</button>
    </div>

    <div class="card" v-if="shouldPrompt">
      <h3>さらに快適に：アプリ登録</h3>
      <p>無料時間を超えました。1タップ登録で次回からスムーズに。</p>
      <button class="btn primary" @click="goRegister">登録に進む</button>
    </div>

    <div v-if="error" style="margin-top:1rem; color:#fca5a5;">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { api } from '@/api'
import FreeTimer from '@/components/FreeTimer.vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const session_id = Number(route.query.session_id)
const store_id = Number(route.query.store_id)
const freeLimit = Number(route.query.free || 15)

const used = ref(0)
const freeRemaining = ref(freeLimit)
const shouldPrompt = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
let timer: number | undefined

onMounted(() => {
  // 自動ハートビート（3秒毎）
  timer = window.setInterval(() => beat(), 3000)
})
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})

async function beat() {
  try {
    loading.value = true
    const res = await api.heartbeat(session_id)
    used.value = res.usedMinutes
    freeRemaining.value = res.freeRemaining
    shouldPrompt.value = !!res.shouldPromptRegister
  } catch (e:any) {
    error.value = e?.message
  } finally {
    loading.value = false
  }
}

function goRegister() {
  router.push({ path: '/register', query: { session_id }})
}

async function finish() {
  try {
    loading.value = true
    const res = await api.settle(session_id)
    await api.close(session_id)
    router.push({ path: '/pay-result', query: {
      store_id,
      minutes_billable: String(res.minutes_billable),
      amount: String(res.amount),
      share: String(res.store_share),
      fee: String(res.protocol_fee)
    }})
  } catch (e:any) {
    error.value = e?.message
  } finally {
    loading.value = false
  }
}
</script>
