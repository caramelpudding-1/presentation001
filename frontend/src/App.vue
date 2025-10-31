<template>
  <div class="app">
    <header class="topbar">
      <h1>Den-TouchNet Demo</h1>
      <nav class="nav">
        <RouterLink to="/">Tap</RouterLink>
        <RouterLink to="/store/dashboard?store_id=1">Store</RouterLink>
        <RouterLink to="/admin/ledger">Ledger</RouterLink>
      </nav>
    </header>
    <main class="container">
      <RouterView />
    </main>
    <footer class="foot">© Demo</footer>
  </div>
</template>

<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body, html, #app { height: 100%; margin: 0; font-family: ui-sans-serif, system-ui, sans-serif; }
.app { min-height: 100%; display: grid; grid-template-rows: auto 1fr auto; }
.topbar { display:flex; align-items:center; justify-content:space-between; padding: 0.75rem 1rem; background:#0b1220; border-bottom:1px solid #1f2a44; }
.topbar h1 { font-size: 1.1rem; margin: 0; }
.nav a { color:#cbd5e1; margin-left:1rem; text-decoration:none; }
.nav a.router-link-active { color:#60a5fa; }
.container { padding: 1rem; max-width: 960px; margin: 0 auto; }
.card { background:#0f172a; border:1px solid #1f2a44; border-radius:.5rem; padding:1rem; margin-bottom:1rem; }
.btn { appearance:none; border:1px solid #334155; background:#0b1220; color:#e5e7eb; padding:.6rem .9rem; border-radius:.5rem; cursor:pointer; }
.btn.primary { background:#0369a1; border-color:#0369a1; }
.input { width:100%; padding:.6rem .7rem; background:#0b1220; border:1px solid #334155; color:#e5e7eb; border-radius:.4rem; }
.grid { display:grid; gap:1rem; }
.grid.cols2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
@media (max-width:720px){ .grid.cols2 { grid-template-columns: 1fr; } }
.foot { padding:.75rem; font-size:.85rem; color:#94a3b8; text-align:center; border-top:1px solid #1f2a44; }
.badge { padding: .2rem .5rem; border-radius:.4rem; background:#1e293b; font-size:.8rem; }
</style>
