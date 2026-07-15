<script setup>
</script>

<template>
  <nav class="nav">
    <div class="brand">
      <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 5h-2v6l5 3 .75-1.23L13 12.5V7z"/>
      </svg>
      <router-link to="/" class="site-name">LocalHub</router-link>
    </div>
  </nav>
</template>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: white; /* 반투명 배경 */
  backdrop-filter: blur(6px); /* 선명도 보정 */
  -webkit-backdrop-filter: blur(6px);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  z-index: 9999;
  box-sizing: border-box;
}

/* 브랜드 */
.brand { display:flex; align-items:center; gap:10px; }
.icon { width:28px; height:28px; color: var(--accent); flex-shrink:0; transition: color .18s; }
.site-name {
  font-weight:700;
  color: var(--accent);
  text-decoration:none;
  font-size:16px;
  transition: color .18s;
}
.site-name:hover { color: var(--accent-border, rgba(170,59,255,0.9)); }

/* 네비 안의 링크/텍스트(가려짐 방지) */
.nav a { color: #fff !important; } 
.nav .site-name { color: var(--accent) !important; }

/* 작은 화면 조정 */
@media (max-width: 700px) {
  .nav { height: 50px; padding: 8px 12px; }
  .site-name { font-size:15px; }
}
</style>