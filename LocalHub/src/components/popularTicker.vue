<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { usePosts } from '../composables/usePosts'

const { posts, loading, error, loadTopByViews, loadRecent } = usePosts()
const index = ref(0)
let timer = null

async function init() {
  // 가능한 경우 조회수 기준 상위 로드, 없으면 최근글 로드 fallback
  if (typeof loadTopByViews === 'function') {
    await loadTopByViews(5)
  } else if (typeof loadRecent === 'function') {
    await loadRecent(5)
  }
  index.value = 0
}

onMounted(async () => {
  await init()
  timer = window.setInterval(() => {
    if (!posts.value || posts.value.length === 0) return
    index.value = (index.value + 1) % posts.value.length
  }, 5000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})

function goTo(post) {
  if (!post) return
  // 라우터 사용을 원하면 router.push로 교체하세요
  window.location.href = `/posts/${post.id}`
}
</script>

<template>
  <nav class="popular-ticker" aria-label="실시간 인기 게시글">
    <div v-if="loading" class="ticker-empty">로딩 중…</div>
    <div v-else-if="!posts || posts.length === 0" class="ticker-empty">인기글 없음</div>
    <div v-else class="ticker-single" @click="goTo(posts[index])" tabindex="0" role="link">
      <span class="rank">#{{ index + 1 }}</span>
      <span class="title">{{ posts[index].title }}</span>
      <span class="views">{{ posts[index].view_count ?? 0 }} views</span>
    </div>
  </nav>
</template>

<style scoped>
.popular-ticker{
  position: absolute;
  top: calc(100% + 8px);    /* 검색창 바로 아래 */
  left: 16px;               /* search-overlay의 padding-left 값과 일치시킬 것 */
  width: auto;
  max-width: calc(100% - 32px);
  padding: 0;
  margin: 0;
  z-index: 60;
  pointer-events: auto;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #222;
}

.ticker-single{
  display:flex;
  gap:12px;
  align-items:center;
  padding: 0;
  cursor: pointer;
  background: transparent !important;
  border: none !important;
}

.rank{ color:#f36928; font-weight:800; width:40px; }
.title{ flex:1 1 auto; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:#222; }
.views{ color:#9aa4ad; font-size:12px; margin-left:8px; }

.ticker-empty{ color:#9aa4ad; font-size:13px; padding:2px 0; }
</style>