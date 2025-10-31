<template>
  <div class="card">
    <div class="grid cols2">
      <div>
        <div><span class="badge">FREE残</span></div>
        <h2 style="margin:.4rem 0 0;">{{ freeRemaining }} min</h2>
        <small>used: {{ usedMinutes }} min</small>
      </div>
      <div style="display:flex; align-items:center; justify-content:flex-end;">
        <SignalAnim :strength="signal" />
      </div>
    </div>
    <div class="barwrap" aria-label="Free time progress">
      <div class="bar" :style="{ width: pct + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SignalAnim from './SignalAnim.vue'
const props = defineProps<{ usedMinutes: number, freeRemaining: number }>()
const total = computed(() => props.usedMinutes + props.freeRemaining)
const pct = computed(() => total.value ? Math.min(100, Math.round(props.usedMinutes / total.value * 100)) : 0)
const signal = computed(() => Math.max(1, 5 - Math.floor((props.freeRemaining)/3)))
</script>

<style scoped>
.barwrap { margin-top:.8rem; width:100%; height:10px; background:#1f2a44; border-radius:999px; overflow:hidden; }
.bar { height:100%; background:#22c55e; }
</style>
