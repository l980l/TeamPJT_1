<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 현재 카테고리 (URL param)
const category = ref(route.params.category || '전체')
watch(() => route.params.category, v => category.value = v || '전체')

// 검색 / 페이징 상태
const q = ref('')
const page = ref(1)
const loading = ref(false)
const boards = ref([])

// 탭 목록 (홈/탭과 일치)
const tabs = ['전체', '관광지', '맛집', '축제행사', '꿀팁정보']

function goTab(t){
  // URL에 카테고리 반영 (router로 이동)
  const name = 'board'
  const param = (t === '전체') ? '' : t
  router.push({ name, params: param ? { category: param } : {} })
}

function openPost(id){
  router.push({ name: 'post', params: { id } })
}

async function loadBoards(){
  loading.value = true
  try {
    // 실제 백엔드 API가 있으면 교체하세요.
    // const params = new URLSearchParams({ category: category.value === '전체' ? '' : category.value, q: q.value, page: page.value })
    // const res = await fetch(`/api/boards?${params}`)
    // boards.value = await res.json()

    // 샘플 데이터 (UI 데모 용)
    boards.value = Array.from({length:6}).map((_,i)=>({
      id: i + 1 + (page.value-1)*6,
      tag: (i % 3 === 0) ? '관광지' : (i % 3 === 1) ? '맛집' : '축제행사',
      author: '익명의 작성자',
      date: '2026-07-14 10:30',
      title: `${category.value || '전체'} 예시 게시글 제목 ${i+1}`,
      excerpt: '짧은 요약문: 제공 데이터를 여기에 넣어주세요. 장소, 팁, 접근성 등 간략 설명이 표시됩니다.',
      views: Math.floor(Math.random()*500),
      likes: Math.floor(Math.random()*80)
    })).filter(b => category.value === '전체' || b.tag === category.value)
  } finally {
    loading.value = false
  }
}

function onSearch(){
  page.value = 1
  loadBoards()
}

onMounted(loadBoards)
watch([category, page], loadBoards)
</script>

<template>
  <main class="board-page">
    <header class="board-hero">
      <div class="hero-left">
        <h1 class="page-title">지역 커뮤니티 게시판</h1>
        <p class="subtitle">이웃들이 남긴 알짜배기 실시간 로컬 정보를 검색해 보세요.</p>
      </div>

      <div class="hero-right">
        <div class="search-wrap">
          <input v-model="q" @keyup.enter="onSearch" placeholder="제목이나 내용으로 검색" />
          <button @click="onSearch" class="search-btn">🔍</button>
        </div>
      </div>
    </header>

    <nav class="tabs" role="tablist">
      <button
        v-for="t in tabs"
        :key="t"
        :class="['tab', { active: (t === (category || '전체')) }]"
        @click="goTab(t)"
      >{{ t }}</button>
    </nav>

    <section class="list-wrap">
      <div v-if="loading" class="loading">로딩 중…</div>

      <article v-for="b in boards" :key="b.id" class="post-card">
        <div class="card-head">
          <span :class="['tag', `tag-${b.tag}`]">{{ b.tag }}</span>
          <div class="meta">
            <span class="author">{{ b.author }}</span>
            <span class="dot">·</span>
            <span class="date">{{ b.date }}</span>
          </div>
        </div>

        <h2 class="post-title" @click="openPost(b.id)">{{ b.title }}</h2>
        <p class="excerpt">{{ b.excerpt }}</p>

        <div class="card-foot">
          <div class="counts">
            <span class="views">👁 {{ b.views }}</span>
            <span class="likes">❤ {{ b.likes }}</span>
          </div>
          <button class="detail" @click="openPost(b.id)">자세히 보기 ▷</button>
        </div>
      </article>

      <div v-if="!boards.length && !loading" class="empty">해당 카테고리에 게시글이 없습니다.</div>

      <footer class="pager">
        <button @click="page = Math.max(1, page-1)">이전</button>
        <span>페이지 {{ page }}</span>
        <button @click="page++">다음</button>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.board-page { max-width:1100px; margin:24px auto; padding:0 16px 40px; }

/* 헤더 */
.board-hero { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:18px; }
.hero-left .page-title { margin:0; font-size:26px; font-weight:800; color:#0b2747; }
.hero-left .subtitle { margin:6px 0 0; color:#6b7280; }

/* 검색 */
.search-wrap { display:flex; gap:8px; align-items:center; }
.search-wrap input {
  width:320px; padding:10px 12px; border-radius:24px; border:1px solid #e6e9ef;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}
.search-btn {
  background:#0b76ef; color:#fff; border:none; padding:10px 12px; border-radius:20px; cursor:pointer;
}

/* 탭 */
.tabs { display:flex; gap:10px; padding:12px 0; margin-bottom:12px; }
.tab {
  background:#fff; border:1px solid #eef2f7; padding:8px 14px; border-radius:999px; cursor:pointer; color:#374151;
}
.tab.active { background: linear-gradient(180deg,#eef7ff,#e6f3ff); border-color:#cfe9ff; color:#0b76ef; font-weight:700; }

/* 리스트 */
.list-wrap { display:flex; flex-direction:column; gap:16px; }
.post-card {
  background:#fff; border-radius:12px; padding:18px; border:1px solid #eef2f7;
  box-shadow: 0 6px 18px rgba(12,20,40,0.04);
}
.card-head { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:8px; }
.tag { padding:6px 10px; border-radius:10px; font-size:12px; font-weight:700; color:#fff; }
.tag-관광지 { background:#ff7ab6; }
.tag-맛집 { background:#7dd3fc; color:#03324b; }
.tag-축제행사 { background:#fbd38d; color:#5a3b00; }
.tag-꿀팁정보 { background:#c4b5fd; color:#2b1750; }

.meta { color:#6b7280; font-size:13px; display:flex; gap:6px; align-items:center; }

/* 제목/요약 */
.post-title { margin:6px 0 6px; font-size:18px; color:#0b2747; cursor:pointer; }
.excerpt { margin:0; color:#4b5563; }

/* 풋터: counts + detail */
.card-foot { display:flex; justify-content:space-between; align-items:center; margin-top:12px; }
.counts { color:#6b7280; display:flex; gap:12px; font-size:13px; }
.detail {
  background: transparent; border:none; color:#6b76ff; font-weight:700; cursor:pointer;
}

/* empty/pager */
.empty { text-align:center; padding:24px; color:#6b7280; }
.pager { display:flex; justify-content:center; gap:12px; margin-top:8px; color:#374151; }
.pager button { padding:8px 12px; border-radius:8px; border:1px solid #e6e9ef; background:#fff; cursor:pointer; }

/* 반응형 */
@media (max-width:900px){
  .board-hero { flex-direction:column; align-items:flex-start; gap:12px; }
  .search-wrap input { width:100%; max-width:420px; }
}
</style>