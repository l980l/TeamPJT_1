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
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: transparent;
  border-bottom: none;
  z-index: 120;
  box-sizing: border-box;
}

/* 아이콘/사이트명은 배너 위에서 읽히기 좋은 색으로 변경 */
.icon { width:28px; height:28px; color: #fff; }
.site-name { font-weight:700; color:#fff; text-decoration:none; }
.brand { display:flex; align-items:center; gap:10px; }
</style>