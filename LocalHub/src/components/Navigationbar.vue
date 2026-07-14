<script setup>
const categories = [
  { label: '관광지', path: '/board/관광지' },
  { label: '맛집', path: '/board/맛집' },
  { label: '축제', path: '/board/축제' },
  { label: '꿀팁', path: '/board/꿀팁' }
]
</script>

<template>
  <nav class="nav">
    <div class="brand">
      <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 5h-2v6l5 3 .75-1.23L13 12.5V7z"/>
      </svg>
      <router-link to="/" class="site-name">LocalHub</router-link>
    </div>

    <div class="links">
      <router-link to="/" class="nav-link" active-class="active">홈</router-link>
      <router-link
        v-for="c in categories"
        :key="c.label"
        :to="c.path"
        class="nav-link"
        active-class="active"
      >{{ c.label }}</router-link>
    </div>

    <div class="actions">
      <router-link to="/new" class="create-btn">글쓰기</router-link>
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
.links { display:flex; gap:14px; align-items:center; }
.nav-link { color:#333; text-decoration:none; padding:6px 8px; border-radius:6px; }
.nav-link:hover { background: #f5f7fb; }
.actions { display:flex; align-items:center; gap:10px; }
.create-btn {
  background: #0b76ef;
  color: #fff;
  padding:6px 12px;
  border-radius:8px;
  text-decoration:none;
  font-weight:600;
}
.create-btn:hover { background: #095fc2; }
.active { color:#0b76ef; font-weight:600; background: rgba(11,118,239,0.06); }
</style>