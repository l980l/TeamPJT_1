<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 현재 카테고리 (URL param)
const category = ref(route.params.category || '전체')
watch(() => route.params.category, v => category.value = v || '전체')

// 검색 / 페이징 상태
const q = ref(route.query.q || '')
watch(() => route.query.q, v => { q.value = v || ''; page.value = 1; loadBoards() })
const page = ref(1)
const loading = ref(false)
const boards = ref([])

// 페이징 meta
const total = ref(0)
const perPage = 6
const totalPages = computed(() => Math.max(1, Math.ceil((total.value || 0) / perPage)))
const pages = computed(() => {
  // 단순: 모든 페이지 나열 (필요시 슬라이딩 윈도우로 변경)
  return Array.from({ length: totalPages.value }, (_, i) => i + 1)
})

// 탭 목록
const tabs = ['전체', '관광지', '레포츠', '문화시설', '쇼핑', '숙박', '여행코스', '축제공연행사']

function goTab(t) {
  const name = 'board'
  const param = (t === '전체') ? '' : t
  router.push({ name, params: param ? { category: param } : {} })
}

function openPost(id) {
  router.push({
    name: 'post',
    params: { id },
    query: { category: (category.value && category.value !== '전체') ? category.value : '' }
  })
}

function formatShortDate(raw) {
  if (!raw) return ''
  const d = new Date(raw)
  if (isNaN(d)) return raw
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${mm}.${dd}`
}

async function loadBoards() {
  loading.value = true
  try {
    const params = new URLSearchParams({
      q: q.value || '',
      limit: perPage,
      skip: (page.value - 1) * perPage
    })
    if (category.value && category.value !== '전체') {
      params.set('category', category.value)
    }
    const res = await fetch(`/api/posts?${params.toString()}`)
    if (!res.ok) throw new Error('로드 실패')

    // 응답 처리: header X-Total-Count 우선, 다음 data.total, 다음 items/배열 길이
    const headerTotal = res.headers.get('X-Total-Count')
    const data = await res.json()
    let items = []
    if (Array.isArray(data.items)) items = data.items
    else if (Array.isArray(data)) items = data
    else if (Array.isArray(data.data)) items = data.data
    else items = data.items ?? data.data ?? []

    total.value = headerTotal ? Number(headerTotal) : (data.total ?? (Array.isArray(data) ? data.length : (items.length || 0)))

    // normalize items (if top-level array was returned)
    const list = Array.isArray(items) && items.length ? items : (Array.isArray(data) ? data : [])

    boards.value = list.map(p => ({
      id: p.id,
      tag: p.category || '기타',
      author: p.author || '익명의 작성자',
      date: p.created_at ? p.created_at : '',
      title: p.title,
      excerpt: (p.content || '').slice(0, 120),
      views: p.views ?? 0,
      likes: p.likes ?? 0
    }))
  } catch (e) {
    boards.value = []
    total.value = 0
    console.error(e)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  loadBoards()
}

function goToPage(n) {
  const target = Math.min(Math.max(1, n), totalPages.value)
  page.value = target
}

onMounted(loadBoards)
watch([category, page], loadBoards)
</script>

<template>
  <main class="board-page">
    <header class="board-hero">
      <div class="wrap">
        <div class="head">
          <p class="crumb">홈 &nbsp;›&nbsp; 게시판</p>
          <h1 class="head__title">지역 정보 게시판</h1>
          <p class="subtitle">이웃들이 남긴 알짜배기 실시간 로컬 정보를 검색해 보세요.</p>
        </div>
      </div>

      <div class="hero-search-row">
          <form class="search-wrap" @submit.prevent="onSearch">
            <input v-model="q" type="search" placeholder="제목, 내용으로 검색" />
            <button class="search-btn" type="submit">검색</button>
          </form>
          <router-link
            :to="category && category !== '전체' ? { name: 'new', query: { category: category } } : { name: 'new' }"
            class="create-btn">＋ 글쓰기</router-link>
      </div>
    </header>

    <nav class="tabs" role="tablist">
      <button v-for="t in tabs" :key="t" :class="['tab', { active: (t === (category || '전체')) }]" @click="goTab(t)">{{ t
      }}</button>
    </nav>

    <section class="list-wrap">
      <div v-if="loading" class="loading">로딩 중…</div>

      <!-- API 데이터가 있는 경우 -->
      <template v-if="!loading && boards.length">
        <article v-for="b in boards" :key="b.id" :class="['post-card', `accent-${b.tag}`]">
          <div class="card-head">
            <span :class="['tag', `tag-${b.tag}`]">{{ b.tag }}</span>
            <div class="meta">
              <span class="author">{{ b.author }}</span>
              <span class="dot">·</span>
              <span class="date">{{ formatShortDate(b.date) }}</span>
            </div>
          </div>

          <h2 class="post-title">
            <router-link
              :to="{ name: 'post', params: { id: b.id }, query: { category: (category && category !== '전체') ? category : '' } }"
              class="post-link">
              {{ b.title }}
            </router-link>
          </h2>
          <p class="excerpt">{{ b.excerpt }}</p>

          <div class="card-foot">
            <div class="counts">
              <span class="views">👁 {{ b.views }}</span>
              <span class="likes">❤ {{ b.likes }}</span>
            </div>
            <router-link
              :to="{ name: 'post', params: { id: b.id }, query: { category: (category && category !== '전체') ? category : '' } }"
              class="detail">
              자세히 보기 ▷
            </router-link>
          </div>
        </article>
      </template>

      <template v-else-if="!loading && !boards.length">
        <div class="empty">
          {{ q ? '검색 결과가 없습니다.' : '등록된 게시글이 없습니다.' }}
        </div>
      </template>

      <!-- 숫자 페이저 -->
      <footer class="pager" v-if="totalPages > 1">
        <button @click="goToPage(page - 1)" :disabled="page <= 1">‹</button>

        <button v-for="n in pages" :key="n" :class="['num', { on: n === page }]" @click="goToPage(n)">{{ n }}</button>

        <button @click="goToPage(page + 1)" :disabled="page >= totalPages">›</button>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.post-link {
  color: inherit;
  text-decoration: none;
  display: inline-block;
  width: 100%;
}

.post-link:hover {
  text-decoration: underline;
}

.board-page {
  box-sizing: border-box;
  width: 100%;
  max-width: 1400px;
  margin: 24px auto;
  padding: 0 40px 48px;
}

.board-hero {
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 22px;
  border-bottom: 1px solid #eef2f7;
  text-align: left;
}

.hero-center {
  text-align: center;
}

.hero-search-row {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.hero-search-row .search-wrap {
  width: auto;
  flex: 1 1 auto;
}

.create-btn {
  background: linear-gradient(180deg, #ff8b6a, #ff7a52);
  color: #fff;
  padding: 10px 16px;
  border-radius: 14px;
  text-decoration: none;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 12px 30px rgba(255, 122, 82, 0.16);
  border: none;
}

.search-wrap {
  display: flex;
  gap: 8px;
  align-items: center;
  max-width: 760px;
  width: 100%;
}

.search-wrap input {
  flex: 1 1 auto;
  min-width: 220px;
  max-width: 520px;
  padding: 14px 18px;
  border-radius: 14px;
  border: none;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(6, 10, 30, 0.08);
  color: var(--ink);
  font-size: 14px;
}

/* placeholder 색상 */
.search-wrap input::placeholder {
  color: #bfc8cf;
}

.search-btn,
.create-btn {
  height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  white-space: nowrap;
  flex-shrink: 0;
  box-shadow: 0 10px 22px rgba(6, 10, 30, 0.12);
}

.search-btn {
  background: linear-gradient(180deg, #2b2d3a, #16161d);
  color: #fff;
}

.create-btn {
  background: linear-gradient(180deg, #ff8b6a, #ff7a52);
  color: #fff;
  box-shadow: 0 12px 30px rgba(255, 122, 82, 0.16);
  text-decoration: none;
}

.wrap {
  margin: 0 auto;
  margin-bottom: 22px;
}

.head {
  text-align: left;
  width: 100%;
}

.crumb {
  font-size: 13px;
  color: #a6a6b4;
}

.head__title {
  font-size: 30px;
  line-height: 1.4;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 8px 0 6px;
  padding-bottom: 4px;
  background: linear-gradient(135deg, #1f2430, #4b3f9e);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #6b7280;
  font-size: 14.5px;
}

.tabs {
  display: flex;
  gap: 10px;
  padding: 12px 0;
  margin-bottom: 12px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.tabs::-webkit-scrollbar {
  display: none;
}

.tab {
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #eef2f7;
  padding: 9px 16px;
  border-radius: 999px;
  cursor: pointer;
  color: #6b7280;
  font-weight: 600;
  font-size: 13.5px;
  transition: transform .12s ease, box-shadow .12s ease, color .12s ease, border-color .12s ease;
}

.tab:hover {
  border-color: #d9ddff;
  color: #4b3f9e;
  transform: translateY(-1px);
}

.tab.active {
  background: linear-gradient(135deg, #6b76ff, #4b3f9e);
  border-color: transparent;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 10px 22px rgba(75, 63, 158, 0.22);
}

.list-wrap {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  align-items: stretch;
}

.loading,
.empty,
.pager {
  grid-column: 1 / -1;
}

.post-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 14px;
  padding: 20px 20px 20px 24px;
  border: 1px solid #eef2f7;
  box-shadow: 0 6px 18px rgba(12, 20, 40, 0.04);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.post-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14px;
  bottom: 14px;
  width: 4px;
  border-radius: 4px;
  background: #d7dae6;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(12, 20, 40, 0.10);
  border-color: #e2e4f5;
}

.accent-관광지::before { background: #ff7ab6; }
.accent-맛집::before { background: #7dd3fc; }
.accent-축제공연행사::before { background: #fbd38d; }
.accent-레포츠::before { background: #7ee3b3; }
.accent-문화시설::before { background: #c4b5fd; }
.accent-쇼핑::before { background: #ffd166; }
.accent-숙박::before { background: #90cdf4; }
.accent-여행코스::before { background: #fbb6b6; }

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.tag {
  padding: 6px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.tag-관광지 {
  background: #ff7ab6;
}

.tag-맛집 {
  background: #7dd3fc;
  color: #03324b;
}

.tag-축제공연행사 {
  background: #fbd38d;
  color: #5a3b00;
}

.tag-레포츠 {
  background: #7ee3b3;
  color: #063a2e;
}

.tag-문화시설 {
  background: #c4b5fd;
  color: #2b1750;
}

.tag-쇼핑 {
  background: #ffd166;
  color: #4b2e00;
}

.tag-숙박 {
  background: #90cdf4;
  color: #02263a;
}

.tag-여행코스 {
  background: #fbb6b6;
  color: #3b0f0f;
}

.meta {
  color: #6b7280;
  font-size: 13px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.post-title {
  margin: 4px 0 8px;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.35;
  color: #1a1f2e;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-link:hover {
  color: #4b3f9e;
}

.excerpt {
  margin: 0;
  color: #6b7280;
  font-size: 13.5px;
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f2f3f8;
}

.counts {
  color: #9aa0b3;
  display: flex;
  gap: 12px;
  font-size: 12.5px;
}

.detail {
  background: transparent;
  border: none;
  color: #4b3f9e;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: transform .12s ease;
}

.detail:hover {
  transform: translateX(2px);
}

.empty {
  text-align: center;
  padding: 24px;
  color: #6b7280;
}

.pager {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 18px;
  align-items: center;
}

.pager button,
.num {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: #fff;
  border: 1px solid rgba(230, 230, 235, 0.9);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #9aa4ad;
  box-shadow: 0 6px 12px rgba(6, 10, 30, 0.04);
  font-weight: 600;
}


.pager button[disabled] {
  opacity: 0.45;
  cursor: not-allowed;
}

.num.on {
  background: #5b45d6;
  color: #fff;
  border-color: #5b45d6;
  box-shadow: 0 10px 22px rgba(91, 69, 214, 0.18);
}

@media (max-width:900px) {
  .board-page {
    padding: 0 16px 24px;
  }

  .board-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .hero-search-row {
    flex-direction: column;
    align-items: stretch;
  }

  .create-btn {
    justify-content: center;
  }

  .search-wrap {
    width: 100%;
    display: flex;
    gap: 8px;
  }

  .search-wrap input {
    width: 100%;
    max-width: none;
  }
}
</style>