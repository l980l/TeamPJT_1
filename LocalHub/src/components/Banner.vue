<script setup>
defineProps({
  titleMain: { type: String, default: '지금 서울에서' },
  titleHighlight: { type: String, default: '가장 핫한 힐링 장소는?' },
  subtitle: { type: String, default: '전통과 현대가 공존하는 대한민국의 수도. 한강을 중심으로 펼쳐진 멋진 야경과 풍부한 먹거리...' },
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
      </div>

      <aside class="right">
        <div class="stats">
          <div class="stat">
            <div class="num">{{ statNew }}</div>
            <div class="label">오늘 등록된 새글</div>
          </div>
          <div class="stat">
            <div class="num">{{ statTotal }}</div>
            <div class="label">누적 커뮤니티 정보</div>
          </div>
        </div>

        <div class="category">
          <div class="cat-label">인기 카테고리</div>
          <div class="cat-pill">
            <span class="fire">🔥</span>
            <span>{{ highlightCategory }}</span>
            <router-link to="/board/맛집" class="go-btn">이동하기</router-link>
          </div>
        </div>
      </aside>
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
  color: #fff;
  padding: 36px 24px;
  border-radius: 8px;
  margin: 18px 0;
  box-shadow: 0 10px 30px rgba(11,16,40,0.45);
}

/* 내부 레이아웃 동일 */
.banner-inner {
  display:flex;
  gap:24px;
  align-items:flex-start;
  justify-content:space-between;
  max-width:1200px;
  margin:0 auto;
}
.left { flex:1; min-width:0; }
.kicker {
  display:inline-block;
  background: rgba(255,255,255,0.06);
  padding:6px 12px;
  border-radius:999px;
  font-size:12px;
  margin-bottom:12px;
}

/* "지금 서울에서"를 명확히 흰색으로 고정, 약한 그림자 추가로 가독성 강화 */
.title {
  margin:6px 0 12px;
  line-height:1.05;
  font-weight:800;
  font-size:40px;
  display:flex;
  flex-direction:column;
}
.title .main {
  color: #ffffff;
  text-align:left;
  font-size:40px;
  text-shadow: 0 6px 18px rgba(6,10,30,0.45);
}
.title .highlight {
  font-size:40px;
  color:#bfe0ff;
  margin-top:6px;
  text-align:left;
  text-shadow: 0 3px 10px rgba(6,10,30,0.25);
}

.subtitle {
  color:rgba(255,255,255,0.88);
  max-width:620px;
  margin-bottom:14px;
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
.right { width:260px; display:flex; flex-direction:column; gap:18px; align-items:flex-end; }
.stats { display:flex; gap:12px; width:100%; justify-content:flex-end; }
.stat {
  background: rgba(255,255,255,0.06);
  padding:12px;
  border-radius:10px;
  text-align:center;
  min-width:100px;
}
.stat .num { font-size:20px; font-weight:700; color:#fff; }
.stat .label { font-size:12px; color:rgba(255,255,255,0.8); margin-top:6px; }

.category { width:100%; display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
.cat-label { font-size:12px; color:rgba(255,255,255,0.8); }
.cat-pill {
  background: rgba(255,255,255,0.04);
  padding:10px 12px;
  border-radius:10px;
  display:flex;
  gap:10px;
  align-items:center;
}
.go-btn {
  margin-left:8px;
  background:#fff;
  color:#2b2b2b;
  padding:6px 10px;
  border-radius:8px;
  text-decoration:none;
  font-weight:600;
}

/* 반응형 */
@media (max-width:900px){
  .banner-inner{ flex-direction:column; align-items:flex-start; }
  .right{ width:100%; display:flex; flex-direction:row; justify-content:space-between; }
  .title{ font-size:28px; }
  .title .main, .title .highlight{ font-size:28px; }
}
</style>