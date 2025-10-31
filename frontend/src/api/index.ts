const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5001';

async function http(path: string, init?: RequestInit) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok || json.ok === false) {
    throw new Error(json.error || `HTTP ${res.status}`);
  }
  return json.data;
}

export const api = {
  nfcResolve(tag: string) {
    return http('/api/nfc/resolve', { method: 'POST', body: JSON.stringify({ tag })});
  },
  sessionStart(store_id: number, sticker_id: number, anon_id?: string) {
    return http('/api/session/start', { method: 'POST', body: JSON.stringify({ store_id, sticker_id, anon_id })});
  },
  heartbeat(session_id: number) {
    return http('/api/session/heartbeat', { method: 'POST', body: JSON.stringify({ session_id })});
  },
  shouldPrompt(session_id: number) {
    const p = new URLSearchParams({ session_id: String(session_id) });
    return http('/api/user/prompt-register?' + p.toString());
  },
  register(session_id: number, email?: string, wallet_addr?: string) {
    return http('/api/register', { method: 'POST', body: JSON.stringify({ session_id, email, wallet_addr })});
  },
  settle(session_id: number) {
    return http('/api/depin/settle', { method: 'POST', body: JSON.stringify({ session_id })});
  },
  close(session_id: number) {
    return http('/api/session/close', { method: 'POST', body: JSON.stringify({ session_id })});
  },
  storeDashboard(store_id: number) {
    const p = new URLSearchParams({ store_id: String(store_id) });
    return http('/api/store/dashboard?' + p.toString());
  },
  ledger() {
    return http('/api/admin/ledger');
  }
}
