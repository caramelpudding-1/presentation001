<template>
  <div class="card">
    <h2>決済結果（デモ）</h2>
    <div class="grid cols2">
      <div>
        <h3>Before</h3>
        <p>地下で電波が弱く、QR決済が通らない…</p>
        <div class="badge">失敗</div>
      </div>
      <div>
        <h3>After</h3>
        <p>NFC → 店内Wi-Fiに誘導。決済がスムーズに！</p>
        <div class="badge" style="background:#14532d;">成功</div>
      </div>
    </div>
    <div class="card">
      <h3>清算サマリ</h3>
      <ul>
        <li>課金対象分: <strong>{{ q.minutes_billable }}</strong> 分</li>
        <li>金額: <strong>¥{{ q.amount }}</strong></li>
        <li>店舗取り分: <strong>¥{{ q.share }}</strong></li>
        <li>プロトコル手数料: <strong>¥{{ q.fee }}</strong></li>
      </ul>
      <RouterLink class="btn" :to="`/store/dashboard?store_id=${q.store_id}`">店舗ダッシュボードを見る</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
const q = {
  store_id: Number(route.query.store_id || 1),
  minutes_billable: Number(route.query.minutes_billable || 0),
  amount: Number(route.query.amount || 0),
  share: Number(route.query.share || 0),
  fee: Number(route.query.fee || 0)
}
</script>
