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
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
}
.brand { display:flex; align-items:center; gap:10px; }
.icon { width:28px; height:28px; color:#2b6cb0; }
.site-name { font-weight:700; color:#111; text-decoration:none; }
</style>