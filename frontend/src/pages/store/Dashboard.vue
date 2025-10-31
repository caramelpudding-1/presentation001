<template>
  <div class="card">
    <h2>店舗ダッシュボード</h2>
    <div class="grid cols2">
      <div class="card">
        <div class="badge">今日のセッション</div>
        <h2 style="margin:.4rem 0 0;">{{ data?.total_sessions ?? '-' }}</h2>
      </div>
      <div class="card">
        <div class="badge">平均滞在（分）</div>
        <h2 style="margin:.4rem 0 0;">{{ data?.avg_stay_minutes ?? '-' }}</h2>
      </div>
      <div class="card">
        <div class="badge">売上金額</div>
        <h2 style="margin:.4rem 0 0;">¥{{ data?.revenue_amount ?? '-' }}</h2>
      </div>
      <div class="card">
        <div class="badge">回避できた決済失敗</div>
        <h2 style="margin:.4rem 0 0;">{{ data?.payment_fail_avoided ?? 0 }} / base {{ data?.payment_fail_base ?? 0 }}</h2>
      </div>
    </div>
    <div v-if="error" style="color:#fca5a5;">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { api } from '@/api'
import { useRoute } from 'vue-router'
const route = useRoute()
const store_id = Number(route.query.store_id || 1)
const data = ref<any>(null)
const error = ref<string | null>(null)

onMounted(load)
async function load(){
  try { data.value = await api.storeDashboard(store_id) }
  catch(e:any){ error.value = e?.message }
}
</script>
