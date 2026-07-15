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
const tabs = ['전체', '관광지', '레포츠', '문화시설', '쇼핑', '숙박', '여행코스', '축제공연행사']

function goTab(t){
  // URL에 카테고리 반영 (router로 이동)
  const name = 'board'
  const param = (t === '전체') ? '' : t
  router.push({ name, params: param ? { category: param } : {} })
}

function openPost(id){
  router.push({
    name: 'post',
    params: { id },
    query: { category: (category.value && category.value !== '전체') ? category.value : '' }
  })
}

async function loadBoards(){
  loading.value = true
  try {
    const params = new URLSearchParams({
      q: q.value || '',
      // 서버쪽 limit/skip 구현에 맞춰 page->skip 변환 필요하면 조정
      limit: 6,
      skip: (page.value - 1) * 6
    })
    if (category.value && category.value !== '전체') {
      params.set('category', category.value)
    }
    const res = await fetch(`/api/posts?${params.toString()}`)
    if (!res.ok) throw new Error('로드 실패')
    const data = await res.json()
    // API에서 반환하는 필드에 맞춰 매핑
    boards.value = data.map((p,i)=>({
      id: p.id,
      tag: p.category || '기타',
      author: p.author || '익명의 작성자',
      date: p.created_at ? p.created_at : '',
      title: p.title,
      excerpt: (p.content || '').slice(0,120),
      views: p.views || 0,
      likes: 0
    }))
  } catch (e) {
    // 실패 시 기존 모킹 유지(선택)
    boards.value = []
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
      <div class="hero-center">
        <h1 class="page-title">지역 커뮤니티 게시판</h1>
        <p class="subtitle">이웃들이 남긴 알짜배기 실시간 로컬 정보를 검색해 보세요.</p>
      </div>

      <div class="hero-search-row">
        <router-link to="/new" class="create-btn" aria-label="글쓰기">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>

        <div class="search-wrap">
          <input v-model="q" @keyup.enter="onSearch" placeholder="제목이나 내용으로 검색" />
          <button @click="onSearch" class="search-btn">검색</button>
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
.board-page {
  box-sizing: border-box;
  width: 100%;
  max-width: none;
  margin: 24px 0;
  padding: 0 40px 40px;
}

/* 헤더: 중앙 제목 + 우측 정렬 검색행 */
.board-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

/* 제목 중앙 정렬 */
.hero-center {
  text-align: center;
}

/* 검색행: 왼쪽 글쓰기, 오른쪽 검색 */
.hero-search-row {
  width: 100%;
  display: flex;
  justify-content: space-between; /* flex-end -> space-between으로 변경 */
  align-items: center;
  gap: 12px;
}

.create-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #5b6cff;
  color: #fff;
  border-radius: 10px;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.create-btn svg { display: block; }

.create-btn:hover { background: #5b6bffab; }

/* 검색 래퍼는 원래 스타일 유지 (너비 조절) */
.search-wrap {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 데스크탑 입력 너비, 모바일에서 가득 채움 */
.search-wrap input {
  width: 320px;
  max-width: 60vw;
  padding: 10px 12px;
  border-radius: 24px;
  border: 1px solid #e6e9ef;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.search-btn {
  background: #5b6cff;
  color: #fff;
  border: none;
  padding: 10px 12px;
  border-radius: 20px;
  cursor: pointer;
  flex-shrink: 0;
}

/* 반응형: 작은 화면에서는 검색 입력이 가득 */
@media (max-width: 900px) {
  .board-hero { gap: 10px; }
  .hero-search-row { justify-content: flex-end; }
  .search-wrap input { width: 100%; max-width: none; }
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
.tag-축제공연행사 { background:#fbd38d; color:#5a3b00; }
.tag-레포츠 { background:#7ee3b3; color:#063a2e; }
.tag-문화시설 { background:#c4b5fd; color:#2b1750; }
.tag-쇼핑 { background:#ffd166; color:#4b2e00; }
.tag-숙박 { background:#90cdf4; color:#02263a; }
.tag-여행코스 { background:#fbb6b6; color:#3b0f0f; }

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