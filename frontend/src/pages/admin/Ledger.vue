<template>
    <div class="card">
        <h2>DePIN 台帳（最新100）</h2>
        <table style="width:100%; border-collapse:collapse;">
            <thead>
                <tr style="text-align:left; border-bottom:1px solid #1f2a44;">
                    <th>ID</th>
                    <th>Session</th>
                    <th>Minutes</th>
                    <th>Amount</th>
                    <th>StoreShare</th>
                    <th>Fee</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="r in rows" :key="r.id" style="border-bottom:1px solid #111827">
                    <td>{{ r.id }}</td>
                    <td>{{ r.session_id }}</td>
                    <td>{{ r.minutes }}</td>
                    <td>¥{{ r.amount }}</td>
                    <td>¥{{ r.store_share }}</td>
                    <td>¥{{ r.protocol_fee }}</td>
                    <td><small>{{ r.timestamp }}</small></td>
                </tr>
            </tbody>
        </table>
        <div v-if="error" style="margin-top:1rem; color:#fca5a5;">{{ error }}</div>
    </div>
</template>

<script setup lang="ts">
import { api } from '@/api'
const rows = ref<any[]>([])
const error = ref<string | null>(null)
onMounted(async () => {
    try {
        const d = await api.ledger()
        rows.value = d.records ?? []
    } catch (e: any) {
        error.value = e?.message
    }
})
</script>
