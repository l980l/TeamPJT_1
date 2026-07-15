<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import MapCheck from './map_check.vue'
import PopularTicker from './PopularTicker.vue'

const router = useRouter()
const searchQuery = ref('')

function submitSearch(e) {
  e && e.preventDefault()
  const q = (searchQuery.value || '').trim()
  if (!q) return
  router.push({ path: '/board/검색', query: { q } })
}
defineProps({
  titleMain: { type: String, default: '지금 서울에서' },
  titleHighlight: { type: String, default: '가장 핫한 힐링 장소는?' },
  subtitle: { type: String, default: '전통과 현대가 공존하는 대한민국의 수도. 한강을 중심으로 펼쳐진 야경과 풍부한 먹거리를 실제 리뷰와 반응을 기반으로 찾아보세요!' },
  statNew: { type: [Number,String], default: 2 },
  statTotal: { type: [Number,String], default: 3 },
  highlightCategory: { type: String, default: '맛집 정보' }
})
</script>

<template>
  <section class="banner">
    <div class="banner-inner">
      <div class="left">
        <div class="kicker">오늘의 서울 공공데이터 기반 정보포털</div>
        <h1 class="title">
          <span class="main">{{ titleMain }}</span>
          <span class="highlight">{{ titleHighlight }}</span>
        </h1>
        <p class="subtitle">{{ subtitle }}</p>

        <div class="badges">
          <span class="badge">#한강</span>
          <span class="badge">#DDP</span>
          <span class="badge">실시간 기상: 맑음, 27°C</span>
        </div>
        <div class="popular">
          <div class="popular-label">오늘의 인기 카테고리</div>
          <div class="popular-pill">
            <span class="fire">🔥</span>
            <span class="popular-name">{{ highlightCategory }}</span>
            <router-link to="/board/맛집" class="go-btn">이동하기</router-link>
          </div>
        </div>
      </div>

      <aside class="right">
       <mapCheck />
      </aside>
    </div>
      <div class="search-wrapper">
  <form class="search-overlay" @submit="submitSearch" role="search" aria-label="사이트 검색">
    <input v-model="searchQuery" class="search-input" type="search" placeholder="여행지, 명소, 맛집을 검색하세요" />
    <button class="search-btn" type="submit">검색</button>
  <PopularTicker />
  </form>

  <!-- PopularTicker 컴포넌트가 search-wrapper 내부에 있어야 left:0 기준으로 정렬됩니다 -->
  
  </div>
  </section>
</template>

<style scoped>
/* 더 극강의 그라데이션 — 진한 인디고/퍼플 대비 */
.banner {
  background: linear-gradient(135deg,
    #8b61a7 0%,
    #23186e 30%,
    #3a1f7a 70%,
    #1965c2 100%);
  position: relative;
  width: 100%;
  padding: 70px 24px 100px;
  box-sizing: border-box;
  border-radius: 0;
  box-shadow: none;
  overflow: visible;
}

/* 내부 레이아웃 동일 */
.banner-inner {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px; /* 기존 1200 → 1400 (또는 none) */
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
  padding: 0 24px;
}

.left { 
  flex: 1 1 60%;
  min-width: 0;
}

.kicker {
  background: rgba(255,255,255,0.06);
  padding:6px 12px;
  border-radius:999px;
  font-size:12px;
  width: fit-content;
  margin-bottom:12px;
  color: white;
  text-align:left;
}

/* "지금 서울에서"를 명확히 흰색으로 고정, 약한 그림자 추가로 가독성 강화 */
.title {
  margin: 6px 0 12px;
  line-height: 1.05;
  font-weight: 800;
  font-size: 48px;
  display: flex;
  flex-direction: column;
  text-align: left;
}

.title .main {
  color: #ffffff;
  text-align:left;
  font-size:60px;
  font-weight:800;
  text-shadow: 0 6px 18px rgba(6,10,30,0.45);
}

.title .highlight {
  font-size:70px;
  font-weight:900;
  background: linear-gradient(90deg, #ff7e5f, #feb47b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-top:6px;
  text-align:left;
  text-shadow: 0 3px 10px rgba(6,10,30,0.25);
}

.subtitle {
  color:rgba(255,255,255,0.88);
  max-width:620px;
  margin-bottom:18px;
  text-align:left;
}
.badges { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
.badge {
  background: rgba(255,255,255,0.06);
  padding:6px 10px;
  border-radius:999px;
  font-size:12px;
  color:#e6f6ff;
}

/* 오른쪽 사이드 */
.right {
  flex: 0 0 420px; /* 또는 flex: 0 0 40%; 등으로 비율 사용 */
  display: flex;
  flex-direction: column;
  gap: 18px;
  align-items: flex-start;
}

.right > * {
  width: 100%;
  height: 360px;
  min-height: 240px;
  box-sizing: border-box;
}

.stats { 
  display:flex; 
  gap:12px;
  width:100%; 
  justify-content:flex-end; 
}

.stat {
  background: rgba(255,255,255,0.06);
  padding:12px;
  border-radius:10px;
  text-align:center;
  min-width:100px;
}
.stat .num { font-size:20px; font-weight:700; color:#fff; }
.stat .label { font-size:12px; color:rgba(255,255,255,0.8); margin-top:6px; }

.popular {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.popular-label {
  font-size: 12px;
  color: rgba(255,255,255,0.85);
}

.popular-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.04);
  padding: 10px 14px;
  border-radius: 12px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
}

.popular-name {
  color: #fff;
  font-weight: 600;
  font-size: 15px;
}

/* 버튼 디자인을 좀 더 세련되게 변경 (기존 .go-btn 대체 추천) */
.go-btn {
  margin-left: 8px;
  background: #ffffff;
  color: #2b2b2b;
  padding: 8px 14px;
  border-radius: 14px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(16,24,40,0.18);
  transition: transform .14s ease, box-shadow .14s ease;
}
.go-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 28px rgba(16,24,40,0.24);
}

/* 반응형: 좁은 화면에서는 요소들이 쌓이도록 보정 */
@media (max-width: 900px) {
  .popular-pill { width: 100%; justify-content: space-between; }
  .go-btn { margin-left: 0; }
}

/* 반응형 */
/* 반응형: 화면 작아지면 내부 스택, 폰트 축소 */
@media (max-width: 900px) {
  .banner {
    padding: 40px 18px 80px;
  }
  .banner-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 18px;
  }
  .right {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  .title, .title .main, .title .highlight {
    font-size: 28px;
  }
}

.search-overlay {
  position: relative;
  left: auto;
  transform: none;
  bottom: auto;
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
  background: #fff;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  box-sizing: border-box;
}

.search-input {
  flex: 1 1 auto;
  border: none;
  outline: none;
  font-size: 16px;
  padding: 10px;
}

.search-btn {
  background: linear-gradient(90deg, #ff7e5f, #feb47b);
  color: #ffffff;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(16,24,40,0.14);
  transition: transform .14s ease, box-shadow .14s ease, filter .14s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(16,24,40,0.20);
  filter: brightness(1.02);
}

@media (max-width: 900px) {
  .search-overlay { width: calc(100% - 40px); bottom: -28px; padding: 10px; }
  .search-input { font-size: 14px; }
  .search-btn { padding: 8px 12px; font-size: 14px; }
}

.search-container {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -36px;
  width: min(1100px, calc(100% - 80px));
  box-sizing: border-box;
  pointer-events: none; /* wrapper 자체는 클릭 불가, 내부 요소만 가능 */
}

/* 폼은 포인터 이벤트 허용 */
.search-wrapper {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -36px;
  width: min(1100px, calc(100% - 80px));
  box-sizing: border-box;
  pointer-events: none; /* wrapper는 클릭 패스스루, 내부만 상호작용 */
}

/* 내부 요소는 상호작용 허용 */
.search-wrapper .search-overlay,
.search-wrapper > * { pointer-events: auto; }

.search-wrapper .search-overlay { position: relative; z-index: 70; }
.search-wrapper .popular-ticker { z-index: 60; } /* PopularTicker 의 루트 클래스가 popular-ticker 이면 적용 */
</style>