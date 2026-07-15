<script setup>
import NavigationBar from './components/Navigationbar.vue'
import RecentPosts from './components/recent_posts.vue'
import MapCheck from './components/map_check.vue'
</script>

<template>
  <NavigationBar />
  <router-view />
  <div class="widgets" v-if="$route.meta.showWidget">
    <RecentPosts />
  </div>
</template>

<style scoped>
.widgets {
  width: 100%;
  max-width: 1200px;
  margin: 24px auto;
  padding: 16px;
  box-sizing: border-box;
}

/* child component styling via deep selector */
::v-deep(.recent-posts) {
  margin: 0;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

::v-deep(.recent-posts .posts-list) {
  display: grid;
  gap: 10px;
  padding: 0;
  margin: 0;
}

::v-deep(.recent-posts .post-item) {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
  padding: 10px;
  border-radius: 10px;
  transition: transform .12s ease, box-shadow .12s ease;
}

::v-deep(.recent-posts .post-item:hover) {
  transform: translateY(-4px);
  box-shadow: 0 10px 18px rgba(6,10,30,0.28);
}

::v-deep(.recent-posts .post-meta) {
  flex: 0 0 120px;
  text-align: right;
  color: #cfd8df;
  font-size: 13px;
}
</style>