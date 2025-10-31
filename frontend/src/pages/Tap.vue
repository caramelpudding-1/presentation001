<template>
  <div class="card">
    <h2>NFCをタッチ / QRをスキャン</h2>
    <p>Android ChromeならWeb NFC、PCはテストボタンから。</p>
    <div class="grid cols2">
      <button class="btn primary" @click="scanNFC" :disabled="scanning">
        {{ scanning ? 'スキャン中…' : 'NFCスキャン開始' }}
      </button>
      <div class="grid" style="grid-template-columns:repeat(2,1fr); gap:.5rem;">
        <button class="btn" @click="simulate('TAG_GINZA')">Ginzaタグ</button>
        <button class="btn" @click="simulate('TAG_SHIBUYA')">Shibuyaタグ</button>
      </div>
    </div>

    <div v-if="error" style="margin-top:1rem; color:#fca5a5;">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { api } from '@/api'
import { useRouter } from 'vue-router'
const router = useRouter()
const scanning = ref(false)
const error = ref<string | null>(null)

async function afterResolve(tag: string) {
  const info = await api.nfcResolve(tag)
  const start = await api.sessionStart(info.store_id, info.sticker_id, 'demo-visitor')
  router.push({ path: '/wifi', query: {
    session_id: String(start.session_id),
    store_id: String(info.store_id),
    free: String(info.plan.free_minutes)
  }})
}

async function scanNFC() {
  error.value = null
  if (!('NDEFReader' in window)) {
    error.value = 'この端末ではWeb NFCが使えません（PCはテストボタンを使ってください）'
    return
  }
  try {
    scanning.value = true
    // @ts-ignore
    const reader = new NDEFReader()
    await reader.scan()
    // @ts-ignore
    reader.onreading = async (ev) => {
      try {
        const rec = ev.message.records?.[0]
        const tag = (rec && (rec.data || rec.recordType)) || 'UNKNOWN'
        await afterResolve(String(tag))
      } catch (e:any) {
        error.value = e?.message || '読み取りエラー'
      } finally {
        scanning.value = false
      }
    }
  } catch (e:any) {
    error.value = e?.message || 'NFC開始エラー'
    scanning.value = false
  }
}

async function simulate(tag: string) {
  error.value = null
  try { await afterResolve(tag) } catch (e:any) { error.value = e?.message }
}
</script>
