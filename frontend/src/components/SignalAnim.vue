<template>
  <div class="signal" :title="title">
    <div v-for="n in 5" :key="n" class="bar" :style="barStyle(n)"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ strength?: number, title?: string }>()
function barStyle(n: number) {
  const active = (props.strength ?? 5) >= n
  return {
    opacity: active ? 1 : .25,
    height: `${n * 6 + 6}px`,
    animationDelay: `${n * 0.1}s`
  }
}
</script>

<style scoped>
.signal { display:flex; align-items:flex-end; gap:4px; height:48px; }
.bar { width:6px; background:#60a5fa; border-radius:2px; animation: pulse 1.4s infinite ease-in-out; }
@keyframes pulse {
  0%,100% { filter:brightness(0.9) }
  50% { filter:brightness(1.2) }
}
</style>
