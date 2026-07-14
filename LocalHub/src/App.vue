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
    <MapCheck />
  </div>
</template>

<style scoped>
  .widgets {
  display: flex;
  gap: 20px;
  margin: 20px;
}

.widgets > * {
  flex: 1 1 50%;
  min-width: 0;
}

/* 모바일에서 세로 스택 */
@media (max-width: 768px) {
  .widgets {
    flex-direction: column;
  }
}

</style>