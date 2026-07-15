<script setup>
import { ref, onMounted, watch, computed } from 'vue'
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
        <div class="search-wrap">
          <input v-model="q" @keyup.enter="onSearch" placeholder="제목이나 내용으로 검색" />
          <button @click="onSearch" class="search-btn">검색</button>
          <router-link
            :to="category && category !== '전체' ? { name: 'new', query: { category: category } } : { name: 'new' }"
            class="create-btn">＋ 글쓰기</router-link>
        </div>
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
        <article v-for="b in boards" :key="b.id" class="post-card">
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

      <!-- 데이터가 없으면 예시 정적 내용 표시(원본 유지) -->
      <template v-else-if="!loading && !boards.length">
        <div class="table example">
          <div class="thead">
            <span>번호</span><span>제목</span><span>조회</span><span style="text-align:right">작성일</span>
          </div>

          <router-link class="trow" :to="{ name: 'post', params: { id: 7 } }">
            <span class="c-id">7</span>
            <span class="c-title"><span class="tag food">맛집</span><span class="t">성수동 골목 노포 3곳 다녀왔어요<span
                  class="hot">HOT</span></span></span>
            <span class="c-view">👁 142</span>
            <span class="c-date">07.14</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 6 } }">
            <span class="c-id">6</span>
            <span class="c-title"><span class="tag tour">관광지</span><span class="t">비 오는 날 가기 좋은 실내 코스</span></span>
            <span class="c-view">👁 88</span>
            <span class="c-date">07.13</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 5 } }">
            <span class="c-id">5</span>
            <span class="c-title"><span class="tag event">축제·행사</span><span class="t">한강 여름축제 주차 팁 공유합니다<span
                  class="hot">HOT</span></span></span>
            <span class="c-view">👁 256</span>
            <span class="c-date">07.12</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 4 } }">
            <span class="c-id">4</span>
            <span class="c-title"><span class="tag food">맛집</span><span class="t">혼밥하기 편한 곳 추천 받아요</span></span>
            <span class="c-view">👁 73</span>
            <span class="c-date">07.11</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 3 } }">
            <span class="c-id">3</span>
            <span class="c-title"><span class="tag tour">관광지</span><span class="t">경복궁 한복 대여 후기</span></span>
            <span class="c-view">👁 210</span>
            <span class="c-date">07.10</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 2 } }">
            <span class="c-id">2</span>
            <span class="c-title"><span class="tag food">맛집</span><span class="t">광장시장 먹거리 지도 만들어봤어요</span></span>
            <span class="c-view">👁 134</span>
            <span class="c-date">07.09</span>
          </router-link>
          <router-link class="trow" :to="{ name: 'post', params: { id: 1 } }">
            <span class="c-id">1</span>
            <span class="c-title"><span class="tag event">축제·행사</span><span class="t">종로 등불축제 야경 명당 정리</span></span>
            <span class="c-view">👁 189</span>
            <span class="c-date">07.07</span>
          </router-link>
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
  max-width: none;
  margin: 24px 0;
  padding: 0 40px 40px;
}

.board-hero {
  gap: 12px;
  margin-bottom: 18px;
  text-align: left;
}

.hero-center {
  text-align: center;
}

.hero-search-row {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  /* 오른쪽 정렬 */
  align-items: center;
  gap: 12px;
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
  gap: 8px;
  font-weight: 700;
  cursor: pointer;
  border: none;
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
  margin-bottom: 50px;
}

.head {
  text-align: left;
  width: 100%;
}

.crumb {
  font-size: 13px;
  color: var(--ink-faint);
}

.head__title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.tabs {
  display: flex;
  gap: 10px;
  padding: 12px 0;
  margin-bottom: 12px;
}

.tab {
  background: #fff;
  border: 1px solid #eef2f7;
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
  color: #374151;
}

.tab.active {
  background: linear-gradient(180deg, #eef7ff, #e6f3ff);
  border-color: #cfe9ff;
  color: #0b76ef;
  font-weight: 700;
}

.list-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #eef2f7;
  box-shadow: 0 6px 18px rgba(12, 20, 40, 0.04);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
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
  margin: 6px 0 6px;
  font-size: 18px;
  color: #0b2747;
  cursor: pointer;
}

.excerpt {
  margin: 0;
  color: #4b5563;
}

.card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.counts {
  color: #6b7280;
  display: flex;
  gap: 12px;
  font-size: 13px;
}

.detail {
  background: transparent;
  border: none;
  color: #6b76ff;
  font-weight: 700;
  cursor: pointer;
}

.table {
  background: var(--card);
  border: 1px solid #ececf1;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(40, 30, 90, 0.04);
}

.thead {
  display: grid;
  grid-template-columns: 70px 1fr 90px 100px;
  padding: 14px 22px;
  font-size: 12.5px;
  font-weight: 600;
  color: #a6a6b4;
  border-bottom: 1px solid #ececf1;
  background: #faf9fd;
}

.trow {
  display: grid;
  grid-template-columns: 70px 1fr 90px 100px;
  align-items: center;
  padding: 15px 22px;
  border-bottom: 1px solid #ececf1;
  text-decoration: none;
  color: inherit;
}

.trow:hover {
  background: #faf9ff;
}

.c-id {
  color: #a6a6b4;
}

.c-view,
.c-date {
  color: #a6a6b4;
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
  .board-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
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

  .thead {
    grid-template-columns: 44px 1fr 90px;
  }

  .trow {
    grid-template-columns: 44px 1fr 90px;
  }
}
</style>